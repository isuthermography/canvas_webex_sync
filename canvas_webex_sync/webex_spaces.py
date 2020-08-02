class WebexParticipant(object):
    netid=None
    personId=None
    isModerator=None
    team_membership=None # webex team_membership object
    
    def __init__(self,**kwargs):
        # Set attributes according to constructor parameters
        for arg in kwargs:
            if not hasattr(self,arg):
                raise ValueError("particpant does not have a %s attribute" % (arg))
            setattr(self,arg,kwargs[arg])
            pass
        pass

    def __repr__(self):
        return str(self.__dict__)
    
    pass


class WebexSpace(object):
    name=None
    part_moderator_membership_by_netid=None  # Dictionary by netid of (WebexParticipant, group isModerator,membership object) tuples
    roomId=None
    #webex_room=None # webex room object
    

    def __init__(self,**kwargs):
        self.part_moderator_membership_by_netid={}
        # Set attributes according to constructor parameters
        for arg in kwargs:
            if not hasattr(self,arg):
                raise ValueError("participant does not have a %s attribute" % (arg))
            setattr(self,arg,kwargs[arg])
            pass
        pass
    def __repr__(self):
        return str(self.__dict__)
    pass
    


def webex_participants(webexapi,email_suffix,webexteam):
    """webexapi from WebexTeamAPI()
    webexteam an entry from webexapi.teams.list()
"""

    email_suffix_len = len(email_suffix)
    
    webexpart_by_netid={} # dictionary of participants
    webexpart_by_personId={}

    for member in webexapi.team_memberships.list(webexteam.id):
        if member.personDisplayName=="Educonnector.io Reminder Bot":
            continue # ignore Educonnector
        if not(member.personEmail.endswith(email_suffix)):
            print("Warning: Team member %s does not have ISU email address" % (member.personEmail))
            continue
        
        participant=WebexParticipant(netid=member.personEmail[:-email_suffix_len],
                                     personId=member.personId,
                                     isModerator=member.isModerator,
                                     team_membership=member)
        webexpart_by_netid[participant.netid]=participant
        webexpart_by_personId[participant.personId]=participant
        pass
    return (webexpart_by_netid,webexpart_by_personId)

def webex_spaces(webexapi,email_suffix,webexteam,webexpart_by_netid):
    spaces_by_name={}
    email_suffix_len = len(email_suffix)

    for wspace in webexapi.rooms.list():
        if wspace.teamId != webexteam.id:
            continue
        
        part_moderator_membership_by_netid={} # Dictionary of (part,isModerator)
        for memb in webexapi.memberships.list(wspace.id):
            if memb.personDisplayName=="Educonnector.io Reminder Bot" or memb.personEmail.endswith("@webex.bot"):
                continue # ignore Educonnector and webex bot
            if not(memb.personEmail.endswith(email_suffix)):
                print("Warning: Space member %s does not have university email address" % (memb.personEmail))
                continue
            memb_netid = memb.personEmail[:-email_suffix_len]
            part_moderator_membership_by_netid[memb_netid]=(webexpart_by_netid[memb_netid],memb.isModerator,memb)
            pass
        space = WebexSpace(name=wspace.title,
                           part_moderator_membership_by_netid=part_moderator_membership_by_netid,
                           roomId=wspace.id)
        #webex_room=wspace)
        spaces_by_name[space.name]=space
        pass
    
    
    return spaces_by_name
