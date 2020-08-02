import canvasapi.util
from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

from . import canvas_groups

from webexteamssdk import WebexTeamsAPI
from . import webex_spaces



def webex_link_page_content(webexapi,webexteam,group_name,spaces_by_name):
    
    # The team meeting URL doesn't actually seem to work (?)
    
    #webex_team_url="https://teams.webex.com/teams/%s" % (webexteam.id)
    #team_meeting_info = webexapi.rooms.get_meeting_info(spaces_by_name[webexteam.name].roomId)
    #webex_team_meetingurl = team_meeting_info.meetingLink
    #webex_team_meetingphone = team_meeting_info.callInTollNumber
    #webex_team_meetingnumber = team_meeting_info.meetingNumber
    
    
    
    webex_space_url="https://teams.webex.com/spaces/%s" % (spaces_by_name[group_name].roomId)
    space_meeting_info = webexapi.rooms.get_meeting_info(spaces_by_name[group_name].roomId)
    webex_space_meetingurl = space_meeting_info.meetingLink
    webex_space_meetingphone = space_meeting_info.callInTollNumber
    webex_space_meetingnumber = space_meeting_info.meetingNumber
    
    
    #<li>Class/Section site (Webex Team): <a href="%s">%s</a></li>
    #<li>Class/Section Webex meeting: <a href="%s">%s</a></li> or call %s meeting number %s
    
    webexlinks_html = """<h1>Webex Links</h1>
    <ul>
    <li>Group site (Webex Space): <a href="%s">%s</a></li>
    <li>Group Webex meeting: <a href="%s">%s</a> or call %s meeting number %s</li><br/>Note: At least one person may need to login through the group site and start the meeting from there. Try turning off video if you are on a slow Internet link.
    </ul>
<p>
  Tip: When connecting to the Webex space click the pulldown in the upper 
center to show the meeting, whiteboard, messaging, etc.  buttons
</p>""" % (#webex_team_url,webex_team_url,
        #webex_team_meetingurl,webex_team_meetingurl,webex_team_meetingphone,webex_team_meetingnumber,
        webex_space_url,webex_space_url,
        webex_space_meetingurl,webex_space_meetingurl,webex_space_meetingphone,webex_space_meetingnumber)
    return webexlinks_html

def canvas_webex_sync(canvas, webexapi, email_suffix, course_name,canvas_group_category_name):
    course = [c for c in canvas.get_courses() if c.name==course_name][0]
    
    (canvpart_by_netid,
     canvpart_by_canvasid,
     canvpart_by_sortablename
    ) = canvas_groups.canvas_participants(canvas,course)
    
    
    groups_by_name=canvas_groups.canvas_groups(canvas,course,canvas_group_category_name,canvpart_by_canvasid)
    

    # look up webex team
    matching_webexteams = [tm for tm in webexapi.teams.list() if tm.name==course_name]

    if len(matching_webexteams) < 1:
        print("Creating Webex team for \"%s\"..." % (course_name))
        webexteam = webexapi.teams.create(course_name)
        pass
    else:
        print("Found pre-existing Webex team for \"%s\"..." % (course_name))
        webexteam = matching_webexteams[0]
        pass
    
    (webexpart_by_netid,
     webexpart_by_personId
    ) = webex_spaces.webex_participants(webexapi,email_suffix,webexteam)
    

    spaces_by_name = webex_spaces.webex_spaces(webexapi,
                                               email_suffix,
                                               webexteam,
                                               webexpart_by_netid)

    all_participants = set(canvpart_by_netid.keys()) | set(webexpart_by_netid.keys())

    common_participants = set(canvpart_by_netid.keys()) & set(webexpart_by_netid.keys())


    participants_to_remove_from_webex= set(webexpart_by_netid.keys()) - set(canvpart_by_netid.keys())

    participants_to_add_to_webex = set(canvpart_by_netid.keys()) - set(webexpart_by_netid.keys()) 
    

    
    print("Removing participants from webex: %s" % (str(participants_to_remove_from_webex)))
    OK = str(input("OK? [y/N]"))
    if OK.strip()=='y' or OK.strip()=='Y':

        for participant in participants_to_remove_from_webex:
    
            # Not present in Canvas... remove from Webex
            # ... Erase this user from all spaces with the user
            #for spacename in spaces_by_name:
            #    if participant in spaces_by_name[spacename].part_moderator_membership_by_netid:
            #        # Remove from webex
            #        webexapi.memberships.delete(spaces_by_name[spacename].part_moderator_membership_by_netid[participant][2].id)
            #        # Remove from our structure
            #        del spaces_by_name[spacename].part_moderator_membership_by_netid[participant]
            #        pass
            #    
            #    
            #    pass
            
            webexapi.team_memberships.delete(webexpart_by_netid[participant].team_membership.id)
            
            pass
        pass
    
    
    for participant in common_participants:
        # Update moderator status if appropriate
        isModerator = canvpart_by_netid[participant].type in frozenset(["TeacherEnrollment","TaEnrollment"])
        
        if isModerator != webexpart_by_netid[participant].isModerator:
            # Update moderator status
            print("Updating moderator status of %s to %s" % (participant,str(isModerator)))
            webexapi.team_memberships.update(webexpart_by_netid[participant].team_membership.id,isModerator=isModerator)
            pass
        pass
    
    
    print("Adding participants to webex: %s" % (str(participants_to_add_to_webex)))
    OK = str(input("OK? [y/N]"))
    if OK.strip()=='y' or OK.strip()=='Y':
        
        for participant in participants_to_add_to_webex:
            
            
            mship = webexapi.team_memberships.create(webexteam.id,personEmail="%s%s" % (participant,email_suffix),isModerator=canvpart_by_netid[participant].type in frozenset(["TeacherEnrollment","TaEnrollment"]))
            
            pass
        pass
    
    
    # Reload participants/spaces now that
    # we have updated participant lists
    
    (webexpart_by_netid,
     webexpart_by_personId
    ) = webex_spaces.webex_participants(webexapi,email_suffix,webexteam)
    
    
    spaces_by_name = webex_spaces.webex_spaces(webexapi,
                                               email_suffix,
                                               webexteam,
                                               webexpart_by_netid)
    
    webex_space_names = set(spaces_by_name.keys())-set([webexteam.name]) # Ignore "General" space for the team.
    
    
    

    all_groups = set(groups_by_name.keys()) | webex_space_names
    
    common_groups = set(groups_by_name.keys()) & webex_space_names


    groups_to_remove_from_webex= webex_space_names - set(groups_by_name.keys())
    
    groups_to_add_to_webex = set(groups_by_name.keys()) - webex_space_names 
    

    print("Removing groups from webex: %s" % (str(groups_to_remove_from_webex)))
    OK = str(input("OK? [y/N]"))
    if OK.strip()=='y' or OK.strip()=='Y':
        for spacename in groups_to_remove_from_webex:
            space = spaces_by_name[spacename]
            # Remove all memberships in this space
            #for spacemember in space.part_moderator_membership_by_netid:
            #    (part,moderator,membership)=space.part_moderator_membership_by_netid[spacemember]
            #    webexapi.memberships.delete(membership.id)
            #    pass
            
            # Remove the space
            webexapi.rooms.delete(space.roomId)
            
            # Remove from our dictionary
            del spaces_by_name[spacename]
            pass
        pass
    
    
    
    print("Adding groups to webex: %s" % (str(groups_to_add_to_webex)))
    OK = str(input("OK? [y/N]"))
    if OK.strip()=='y' or OK.strip()=='Y':
        for spacename in groups_to_add_to_webex:
            webexapi.rooms.create(spacename,teamId=webexteam.id)
            pass
        groups_need_link_updates=set(groups_to_add_to_webex)
        pass
    else:
        groups_need_link_updates=set([])
        pass
    
    # Update again
    
    spaces_by_name = webex_spaces.webex_spaces(webexapi,
                                               email_suffix,
                                               webexteam,
                                               webexpart_by_netid)
    
    
    webex_space_names = set(spaces_by_name.keys())-set([webexteam.name]) # Ignore "General" space for the team.
    
    all_groups = set(groups_by_name.keys()) | webex_space_names
    
    common_groups = set(groups_by_name.keys()) & webex_space_names
    
    
    # All course staff should be listed as member/moderator of all
    # teams in webex
    
    staff_set = set([participant for participant in webexpart_by_netid if webexpart_by_netid[participant].isModerator ])

    canvas_members_plus_staff_by_group = { group_name: set(groups_by_name[group_name].part_by_netid.keys()) | staff_set for group_name in common_groups }


    # Update webex space memberships
    common_members_by_group = { group_name: canvas_members_plus_staff_by_group[group_name] & set(spaces_by_name[group_name].part_moderator_membership_by_netid.keys())  for group_name in common_groups }

    webex_add_members_by_group = { group_name: canvas_members_plus_staff_by_group[group_name] - set(spaces_by_name[group_name].part_moderator_membership_by_netid.keys())  for group_name in common_groups }

    webex_remove_members_by_group = { group_name: set(spaces_by_name[group_name].part_moderator_membership_by_netid.keys()) - canvas_members_plus_staff_by_group[group_name] for group_name in common_groups }

    print("Group membership removals")
    print("-------------------------")
    for group_name in webex_remove_members_by_group:
        if len(webex_remove_members_by_group[group_name]) > 0:
            print("%15s remove %s" % (group_name,webex_remove_members_by_group[group_name]))
            pass
        pass
    OK = str(input("OK? [y/N]"))
    if OK.strip()=='y' or OK.strip()=='Y':
        for group_name in webex_remove_members_by_group:
            for member_to_remove in webex_remove_members_by_group[group_name]:
                webexapi.memberships.delete(spaces_by_name[group_name].part_moderator_membership_by_netid[member_to_remove][2].id)
                pass
            
            pass
        pass
    
    
    # Update moderator status
    # Space moderation seems to be obsolete or not supported
    #for group_name in common_members_by_group:
    #    for member_to_update in common_members_by_group[group_name]:
    #        isModerator = canvpart_by_netid[member_to_update].type in frozenset(["TeacherEnrollment","TaEnrollment"])
    #
    #        if webexpart_by_netid[member_to_update].isModerator != isModerator:
    #            webexapi.memberships.update(spaces_by_name[group_name].part_moderator_membership_by_netid[member_to_update][2].id,isModerator=isModerator)
    #            pass
    #        pass
    #    pass
    
    

    print("Group membership additions")
    print("-------------------------")
    for group_name in webex_add_members_by_group:
        if len(webex_add_members_by_group[group_name]) > 0:
            print("%15s add %s" % (group_name,webex_add_members_by_group[group_name]))
            pass
        pass
    OK = str(input("OK? [y/N]"))
    if OK.strip()=='y' or OK.strip()=='Y':
        for group_name in webex_add_members_by_group:
            for member_to_add in webex_add_members_by_group[group_name]:
                #isModerator = canvpart_by_netid[member_to_add].type in frozenset(["TeacherEnrollment","TaEnrollment"])
                
                webexapi.memberships.create(spaces_by_name[group_name].roomId,personId=webexpart_by_netid[member_to_add].personId) # ,isModerator=isModerator)
                pass
            
            pass
        pass
    
    
    

    build_webex_links_page=set(groups_need_link_updates)

    

    # Check for webex links group pages on Canvas
    for group_name in common_groups:
        webex_links = [page for page in groups_by_name[group_name].canv_group.get_pages() if page.title=="Webex Links"] # list of links pages (should be empty or length-1
        if len(webex_links) < 1:
            build_webex_links_page.add(group_name)
            pass
        pass
    
    print("Create Webex Links pages for groups: %s" % (str(build_webex_links_page)))
    OK = str(input("OK or Rebuild All? [y/N/r]"))
    if OK.strip().lower()=='y' or OK.strip().lower()=='r':
        if OK.strip().lower()=='r':
            build_webex_links_page=set(common_groups)
            pass
        
        for group_name in build_webex_links_page:
            webex_links = [page for page in groups_by_name[group_name].canv_group.get_pages() if page.title=="Webex Links"] # list of links pages (should be empty or length-1
            if len(webex_links) < 1:
                webex_links_page = groups_by_name[group_name].canv_group.create_page(wiki_page={"title": "Webex Links"})
                pass
            else:
                webex_links_page = webex_links[0]
                pass
            
            # Check for front page
            set_front_page=True
            try:
                groups_by_name[group_name].canv_group.show_front_page()
                set_front_page=False # if we got here, there is already a front page
                pass
            except ResourceDoesNotExist:
                pass
            
            
            page_edits = {
                "wiki_page[body]": webex_link_page_content(webexapi,webexteam,group_name,spaces_by_name)
            }
            if set_front_page:  # Set this to be the front page if there is no other front page
                page_edits["wiki_page[front_page]"]="true"
                pass
            
            
            # This next line should work, but doesn't because of a bug
            # in the canvasapi v1.0.0.. Page.edit() is inoperable on group pages.
            #webex_links_page.edit(**page_edits)
            # So we do the low-level call instead
            res=webex_links_page._requester.request("PUT","groups/%s/pages/%s" % (webex_links_page.parent_id,webex_links_page.url),_kwargs=canvasapi.util.combine_kwargs(**page_edits))
        
            groups_by_name[group_name].canv_group.create_discussion_topic(title="Webex Links page automatically (re)generated",message="The Webex Links page was automatically generated or re-generated by a script. Try clicking on the \"Pages\" link to see the Webex links",is_announcement=True)
            
            pass
        
        pass
    print("Sync complete.")
    
    return (course,
            canvpart_by_netid,
            groups_by_name,
            webexteam,
            webexpart_by_netid,
            spaces_by_name,
            staff_set)
