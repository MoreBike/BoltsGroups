#!/usr/bin/env python
import csv
import argparse
import os
# import glob
import sys
import json

# our local imports
import config

iterations = 3
times_to_try_logging_in = 1

##############################################################
# Parse Arguments and get things set up
##############################################################
parser = argparse.ArgumentParser(description="Example: ./getRidersFromTeamApp.py --date 20210713")
parser.add_argument('--date', required=True, dest='practice_date', metavar='\"DATE\"', help='DATE is the day of the practice in the form YYYYMMDD"')
args = parser.parse_args()

this_directory = os.path.dirname(os.path.abspath(__file__))
working_directory = f"{this_directory}/{args.practice_date}"

# Extract the info on the practice
event_url = ""
eventID = ""
with open(config.event_list, newline='') as csvfile:
    my_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    # skip the header line
    next(my_reader)
    for row in my_reader:
        eventName = row[0]
#        if not eventName == "Practice":
#            continue
        eventDate = row[1].replace("-", "")
        if not eventDate == args.practice_date:
            continue
        eventID = row[13]
        break

if len(eventID) < 1:
    print("Could not find event")
    exit(1)
# print(event_url)

if not os.path.isdir(args.practice_date):
  os.mkdir(args.practice_date)
#os.chdir(args.practice_date)

dome = f"./getRidersFromTeamApp.sh -f {args.practice_date}/event_replies.json -e {eventID}"
os.system(dome)
