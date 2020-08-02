from canvasapi import Canvas
from webexteamssdk import WebexTeamsAPI

from canvas_webex_sync.canvas_webex_sync import canvas_webex_sync


CANVAS_API_URL="https://canvas.iastate.edu"
# See: https://canvasapi.readthedocs.io/en/stable/


# Obtain CANVAS_API_KEY by going to your Canvas
# account settings, scrolling to "Approved Integrations"
# and selecting "New Access Token" These tokens will last
# according to the expiration selected when you create
# them. 
CANVAS_API_KEY="PUT YOUR CANVAS API KEY HERE"


# Webex access tokens last only 12 hours. To obtain a Webex access
# token, login to https://developer.webex.com. Then click on
# "Docs" and browse to the "Getting Started" page. You can grab
# your personal access token in the "Authentication" section.
webex_access_token="PUT YOUR WEBEX ACCESS TOKEN HERE"

course_name="My Canvas course name"
canvas_group_category_name = "Canvas group" # Name of the Canvas group set of interest
email_suffix="@iastate.edu" # ... suffix that converts User ID's to email addresses registered with Webex



canvas = Canvas(CANVAS_API_URL,CANVAS_API_KEY)

webexapi=WebexTeamsAPI(access_token=webex_access_token)


(
    course,
    canvpart_by_netid,
    groups_by_name,
    webexteam,
    webexpart_by_netid,
    spaces_by_name,
    staff_set
) = canvas_webex_sync(canvas, webexapi, email_suffix, course_name, canvas_group_category_name)

