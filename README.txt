canvas_webex_sync documentation
-------------------------------

canvas_webex_sync is a tool for syncing Canvas
group assignments to Webex Team spaces. (https://teams.webex.com)

Please note that this tool is not endorsed or authorized by
Canvas, Webex, or anyone else. 

While Canvas is supposed to be able to sync to Webex via the
"Education Connector", this is not currently functional at
Iowa State.

canvas_webex_sync allows you to create Webex spaces that follow
a course's Canvas groups, without requiring direct integration
between Canvas and Webex. 

It can be run at the start of the semester, then re-run
as needed to update the Webex teams nondestructively
if the group assignments change.

It also creates a page within each Canvas group titled
"Webex Links" with links to the corresponding Webex space
and Webex meeting. A group announcement is also automatically
created. 

It assumes the user names registered into canvas map to
email addresses registered to Webex via a simple suffix,
e.g. "@iastate.edu".


Installation instructions
-------------------------
Requires: Python 3.x (Anaconda suggested on most platforms)
From a suitable (Anaconda) command prompt, change to the
directory where you have placed the canvas_webex_sync files,
then install prerequisite packages (canvasapi, webexteamssdk),
and finally run the setup script: 
  pip install canvasapi
  pip install webexteamssdk
  python setup.py install

The above commands may need to be run with the same permissions
as the Python installation (e.g. as Administrator or root for
a central Python installation).


Running canvas_webex_sync
-------------------------
Copy and modify the script in the examples/ directory. You will
need to obtain and insert your own CANVAS_API_KEY and your own
webex_access_token. See the script comments for instructions.
You will also need to set the course_name variable.

Then run your modified script using python. It works fine from the
command line, e.g. "python run_sync.py" from Spyder or Jupyter
qtconsole, e.g. "%run run_sync.py"

The script will ask you to confirm most major or potentially
risky steps. You will need to explicity respond with "y".

It is generally safe to rerun canvas_webex_sync again, and it 
will offer to propagate any class or group enrollment changes
from Canvas over to Webex.

Please note that it will not propagate a renamed group very
effectively (delete the old group, create a new group). If
you want to propagate a rename, perform the rename manually
in Webex Teams. Then it should be possible to safely rerun
canvas_webex_sync.

As always, use these tools at your own risk.

