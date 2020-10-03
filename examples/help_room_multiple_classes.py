from canvasapi import Canvas
from webexteamssdk import WebexTeamsAPI

from canvas_webex_sync.canvas_webex_sync import canvas_webex_sync
from canvas_webex_sync.canvas_webex_sync import sync_participants_to_webexteam
from canvas_webex_sync.canvas_webex_sync import sync_webex_spaces
from canvas_webex_sync.canvas_webex_sync import sync_webex_memberships
from canvas_webex_sync import canvas_groups
from canvas_webex_sync import webex_spaces


# The purpose of this example is to illustrate creation and
# synchronization of Webex Teams help rooms that are open to
# students across several canvas courses. 


CANVAS_API_URL="https://canvas.iastate.edu"
# See: https://canvasapi.readthedocs.io/en/stable/


# Obtain CANVAS_API_KEY by going to your Canvas
# account settings, scrolling to "Approved Integrations"
# and selecting "New Access Token" These tokens will last
# according to the expiration selected when you create
# them. 
CANVAS_API_KEY=""


# Webex access tokens last only 12 hours. To obtain a Webex access
# token, login to https://developer.webex.com. Then click on
# "Docs" and browse to the "Getting Started" page. You can grab
# your personal access token in the "Authentication" section.
webex_access_token=""


# Names of the Canvas courses
course_name_13="Canvas Course Name 13"
course_name_245="Canvas Course Name 245"
course_name_123h="Canvas Course Name 123H"

# Name of the Webex Team to create/sync
helpteam_name = "Help Spaces for Canvas Course"

strip_netids=[] # list of netids (email addresses without suffix) to strip for the generated team 
ignore_netids=[] # list of netids (email addresses without suffix) to ignore (not sync)


# Names of the spaces to create within the Webex Team.
# All students are given access to all of these spaces
helpspaces=set(["Help Space 1","Help Space 2","Help Space 3"])

email_suffix="@myschool.edu" # ... suffix that converts User ID's to email addresses registered with Webex



# Connect to Canvas and Webex Teams
canvas = Canvas(CANVAS_API_URL,CANVAS_API_KEY)
webexapi=WebexTeamsAPI(access_token=webex_access_token)


# Look up the 3 canvas courses
course_13 = canvas_groups.course_by_name(canvas,course_name_13)
course_245 = canvas_groups.course_by_name(canvas,course_name_245)
course_123h = canvas_groups.course_by_name(canvas,course_name_123h)


# Get the enrollments and staff for the Canvas courses
(canvpart_by_netid_13,
 canvpart_by_canvasid_13,
 canvpart_by_sortablename_13
 ) = canvas_groups.canvas_participants(canvas,course_13)

(canvpart_by_netid_245,
 canvpart_by_canvasid_245,
 canvpart_by_sortablename_245
 ) = canvas_groups.canvas_participants(canvas,course_245)

(canvpart_by_netid_123h,
 canvpart_by_canvasid_123h,
 canvpart_by_sortablename_123h
 ) = canvas_groups.canvas_participants(canvas,course_123h)

# Merge participant databases from the Canvas courses
# (dictionary of Canvas participants, indexed by netid)
canvpart_by_netid = { **canvpart_by_netid_13,
                      **canvpart_by_netid_245,
                      **canvpart_by_netid_123h }

# Create/Sync Webex team named accroding helpteam_name with
# members as specified in canvpart_by_netid dictionary 
webexteam = sync_participants_to_webexteam(webexapi,canvpart_by_netid,email_suffix,helpteam_name,ignore_netids,strip_netids)

# Get webex participant list
(webexpart_by_netid,
 webexpart_by_personId,
 staff_set
 ) = webex_spaces.webex_participants(webexapi,email_suffix,webexteam,ignore_netids,strip_netids)



ignore_spacenames = set([]) # set of spacenames to ignore (not offer to remove if present and unexpected)

# Create/Sync Webex Spaces given by helpspaces
sync_webex_spaces(webexapi,email_suffix,webexteam,webexpart_by_netid,helpspaces,
                  ignore_spacenames=ignore_spacenames)


# Look up list of spaces
spaces_by_name = webex_spaces.webex_spaces(webexapi,
                                           email_suffix,
                                           webexteam,
                                           webexpart_by_netid)

# Create dictionary by spacename of desired members of each space
canvas_members_plus_staff_by_helpspace = { spacename: (set(canvpart_by_netid.keys()) | staff_set) - set(ignore_netids) - set(strip_netids)  for spacename in helpspaces }

# Create dictionary by spacename of members that need to be added to each space
webex_add_members_by_group = { spacename: canvas_members_plus_staff_by_helpspace[spacename] - set(spaces_by_name[spacename].part_moderator_membership_by_netid.keys())  for spacename in helpspaces }

# Create dictionary by spacename of members that need to be removed from each space
webex_remove_members_by_group = { spacename: set(spaces_by_name[spacename].part_moderator_membership_by_netid.keys()) - (canvas_members_plus_staff_by_helpspace[spacename]-set(strip_netids)) - set(ignore_netids) for spacename in helpspaces }

# Sync the space memberships according to webex_add_members_by_group and webex_remove_members_by_group
sync_webex_memberships(webexapi,spaces_by_name,webexpart_by_netid,
                       webex_add_members_by_group,webex_remove_members_by_group)


