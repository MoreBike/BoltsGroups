Install Instructions
====================

Python Setup
------------
* Create a python virtual environment by doing "python -m venv .venv"
* Start the virtual environment by doing "source .venv/bin/activate"
* Install pygsheets with "pip install pygsheets"
* Leave the virtual environment by typing "deactivate"

 
TeamApp Instructions
--------------------
You will need to do the following from a logged in TeamApp session

1. Download the events by going to the Events page and exporting it as a CSV
   file.  Save it as events-2025.csv.

   Note 1: This value is set in config.py if you want to change it.
   
   Note 2: If you add events, you will need to download a new version of this
           file.

2. Open the developer tools window of your browser (often F12) and click the
   network tab at the top.  Browse to an event, click on the "yes" riders,
   and then in the submenu for that page choose CSV report.  Select the
   request and then find the "Request Headers" section.  There will be a
   cookie for "ta_auth_token".  Save that value in the TA_AUTH_TOKEN line in
   the getRidersFromTeamApp.sh file.

   Note: Yes, I know I should put this in the config.py file to make this nicer but
         this was kinda rough and ready.


Google Sheets
-------------
This script takes a google sheet as input and creates a sheet as output.  The
input sheet has a tab for coaches and a tab for riders and their groups.  A
word about each of these sheets

Team Sheet:
* Coaches have names, levels, TeamApp names, and group preferences
* Riders have names, grades, groups, and team app names
* Config: You will ned to set the value of
          "pygsheets_coaches_riders_spreadsheet" in config.py.  It tells the
          scripts where to find the relevant sheet.  This can be found in the
          URL for your team sheet.

Output:
* The created sheet is matches riders into groups and assigns coaches
* Config: You will ned to set the value of "pygsheets_folder_for_practices"
          in config.py.  It tells the the scrypts where to put he output
          sheet.  This can be found in the URL for the google drive directory
          where you want your files to go.

