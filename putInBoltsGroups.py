#!/usr/bin/env python
import csv
import argparse
import xlwt
import pygsheets
import json
from pprint import pprint
import random
import config
import commonFunctions
import sys

    
##############################################################
# Parse Arguments and get things set up
##############################################################
parser = argparse.ArgumentParser(description="Example: ./putInBoltsGroups.py YESFILE.csv")
parser.add_argument('infile', metavar='\"file\"', help='file to be parsed')
parser.add_argument('--date', required=True, dest='practice_date', metavar='\"DATE\"', help='DATE is the day of the practice in the form YYYYMMDD"')
args = parser.parse_args()

# We take the seed as the practice date so that all random calls will be the same each time I run this program
my_seed = int(args.practice_date)
commonFunctions.eprint(my_seed)
random.seed(my_seed)
# Note: Subroutines are objects and can have variables
commonFunctions.print_random_state.saved_random_state = random.getstate()
commonFunctions.print_random_state("Initial state")

# Service accounts method for Google that got locked out
gc = pygsheets.authorize(service_file=config.pygsheets_service_file)

# Open Coaches and Riders Spreadsheet
sh = gc.open_by_key(config.pygsheets_coaches_riders_spreadsheet)

# Note: To just have the groups, use group_names[1:]
group_names = config.group_names
practices_per_set = config.practices_per_set # This is the number I picked of practices before repeating

all_team_app_entries = {}
# go through the "Bolts Grouping 2023" sheet and create 3 dicts:
## From Riders Page:
### one with "Team App Name" (column 5) as key and group (column 4) as value
### one with "Team App Name" (column 5) as key and "rider" as value
### one with "Team App Name" (column 5) as key and First/Last name as value ("column 1" "column 2")
rider_name = {}
rider_group = {}
# Ok, this is lame, but I need the Riders sheet to be the first one....
riders_worksheet = sh[0]
riders_matrix = riders_worksheet.get_all_values()
row_number = 1
while len(riders_matrix[row_number][0]) > 0:
    row = riders_matrix[row_number]
    teamAppID = row[4]
    name = row[1]+", "+row[0]
    group = row[3]
    rider_name[teamAppID] = name
    rider_group[teamAppID] = group
    all_team_app_entries[teamAppID] = "rider"
    row_number += 1
 
## From Coaches Page
### one with "Team App Name" (column 3) as key and level (column 2) as value
### one with "Team App Name" (column 3) as key and "coach" 
### one with "Team App Name" (column 3) as key and row number
### one with "Team App Name" (column 3) as key and Name as value (column 1)
### one with "Team App Name" (column 3) as first key, "BOLTS!" (and Avoid) as second key, and pref count as values
### one with "Team App Name" (column 3) as first key, "BOLTS!" as second key, and practices worked as values
coach_name = {}
coach_level = {}
coach_group_preference = {}
coach_group_completed = {}
coach_row_number = {}

# Coaches Worksheet - needs to be the second one
# Note: coaches_matrix is indexed from 0 while sheets from pygsheets are indexed from 1
coaches_worksheet = sh[1]
coaches_matrix = coaches_worksheet.get_all_values()
# pprint(coaches_matrix)    

# This clears out data if it was there from running this multiple times
date_found = False
date_found = commonFunctions.find_and_clear_column_for_coach_data(coaches_worksheet, coaches_matrix, args.practice_date, True)[1]

# If we had already filled in this date - rerun to pull updated values
if date_found:
    coaches_matrix = coaches_worksheet.get_all_values()
# pprint(coaches_matrix)    
row_number = 1
while len(coaches_matrix[row_number][0]) > 0:
    row = coaches_matrix[row_number]
    teamAppID = row[3]
    coach_row_number[teamAppID] = row_number
    name = f"{row[0]}, {row[1]}"
    level = row[2]
    coach_name[teamAppID] = name
    coach_level[teamAppID] = level
    coach_group_preference[teamAppID] = {}
    coach_group_preference[teamAppID]["B"] = int(row[4])
    coach_group_preference[teamAppID]["O"] = int(row[5])
    coach_group_preference[teamAppID]["L"] = int(row[6])
    coach_group_preference[teamAppID]["T"] = int(row[7])
    coach_group_preference[teamAppID]["S"] = int(row[8])
    coach_group_preference[teamAppID]["!"] = int(row[9])
    coach_group_preference[teamAppID]["Avoid"] = row[11]
    coach_group_completed[teamAppID] = {}
    coach_group_completed[teamAppID]["B"] = int(row[12])
    coach_group_completed[teamAppID]["O"] = int(row[13])
    coach_group_completed[teamAppID]["L"] = int(row[14])
    coach_group_completed[teamAppID]["T"] = int(row[15])
    coach_group_completed[teamAppID]["S"] = int(row[16])
    coach_group_completed[teamAppID]["!"] = int(row[17])
    all_team_app_entries[teamAppID] = "coach"
    row_number += 1
coaches_total_rows = row_number - 1
#commonFunctions.eprint("coach_group_completed")
#commonFunctions.epprint(coach_group_completed)
#commonFunctions.eprint("coach_group_preference")
#commonFunctions.epprint(coach_group_preference)


# go through the yes response file
## create arrays for each of the groups
# groups = {'Coaches':[], 'B':[], 'O':[], 'L':[], 'T':[], 'S':[], '!':[]}
groups = {}
coaches_attending = {}
coaches_attending['level1'] = {}
coaches_attending['leads'] = {}
unknown = []
for group in group_names:
    groups[group] = []
count_entries = 0


with open(args.infile, "r") as read_file:
    riders_json = json.load(read_file)
    
# We know this works because we checked it in the downloading script
for rider_data in riders_json["sections"][0]["items"]:
    teamAppID = rider_data['title']
    count_entries += 1
    if teamAppID in all_team_app_entries:
        if(all_team_app_entries[teamAppID] == "coach"):
            coach_details = f"Level {coach_level[teamAppID]} - {coach_name[teamAppID]}"
            groups['Coaches'].append(coach_details)
            if (len(coach_level[teamAppID]) > 0) and (int(coach_level[teamAppID]) > 1):
                coaches_attending['leads'][teamAppID] = coach_details
            else:
                coaches_attending['level1'][teamAppID] = coach_details
        else:
            groups[rider_group[teamAppID]].append(rider_name[teamAppID])
    else:
        unknown.append(teamAppID)
        

# prioritze groups according to size
group_need = {}        
for group in group_names[1:]:
    riders_in_group = len(groups[group])
    if riders_in_group > 0:
        group_need[group] = riders_in_group 
group_priority = sorted(group_need, key=group_need.get, reverse=True)



# TODO: I could cut this down to just those attending this week

# Adjust coach_group_preference to account for previous practices
coach_group_prefs_with_practices_removed = {}
for teamAppID in coach_group_completed:

    # First calculate how many "sets" of practices have been completed
    #  for this coach (Note: this will be different for every coach
    #  depending on how regularly they attend)
    coach_total_practices = 0
    coach_group_prefs_with_practices_removed[teamAppID] = {}
    for group in group_names[1:]:
        coach_total_practices += coach_group_completed[teamAppID][group]
    coach_completed_sets = int(coach_total_practices / practices_per_set)

    # Then pull out of the completed practices the expected number of
    #  practices according to preference
    for group in group_names[1:]:
        coach_group_completed[teamAppID][group] -= coach_group_preference[teamAppID][group]*coach_completed_sets

    # In coach_group_completed we have (roughly) how many of the
    #  current set have been done, so we can remove that number from
    #  coach_group_preference to see what groups that coach still has
    #  to do
    for group in group_names[1:]:
        coach_group_prefs_with_practices_removed[teamAppID][group] = coach_group_preference[teamAppID][group] - coach_group_completed[teamAppID][group]
#commonFunctions.eprint("coach_group_prefs_with_practices_removed")
#commonFunctions.epprint(coach_group_prefs_with_practices_removed)

# For any coach who has kids they want to avoid, we set their
# coach_group_prefs_with_practices_removed value to -1
for teamAppID in coach_group_prefs_with_practices_removed:
    if len(coach_group_preference[teamAppID]["Avoid"]) < 1:
        continue
    kids_to_avoid = [x.strip() for x in coach_group_preference[teamAppID]["Avoid"].split(",") ]
    # commonFunctions.eprint("kids_to_avoid:", kids_to_avoid)
    for kid in kids_to_avoid:
        if kid not in all_team_app_entries:
            commonFunctions.eprint(f"Kid to avoid not a teamapp id: {kid}")
        for group in groups:
            if kid in groups[group]:
                coach_group_prefs_with_practices_removed[teamAppID][group] = -1
                commonFunctions.eprint(f"Avoiding putting f{teamAppID} with their kid {kid}")
        


# Next we assign coaches to groups
## - We make two passes - one for level 1 coaches and one for levels 2/3
## - The logic in each will be the same
## -- For each coach, build a list of groups they can ride with
## -- Check that each group has at least one coach that can ride with them
## -- If so, randomly select a coach for each group
## --- of the remaining coaches, repeat starting with the group that has the most need
## -- If not, figure out which coaches are possible (but have done that group too much), report it, and pick the one with the least over
## --- We consider these one time tweaks and just note it and move on - they will be over but that group will get ignored until they catch up 

# Figure out what coaches can handle what groups
# - repeat for level 1 and level 2/3
coach_can_handle_group = {}
for level in coaches_attending:
    coach_can_handle_group[level] = {}
    for group in group_names[1:]:
        coach_can_handle_group[level][group] = {}
    for teamAppID in coaches_attending[level]: 
        for group in group_names[1:]:
            if coach_group_prefs_with_practices_removed[teamAppID][group] > 0:
                coach_can_handle_group[level][group][teamAppID] = coach_group_prefs_with_practices_removed[teamAppID][group]
commonFunctions.epprint(coach_can_handle_group)

coach_final = {}
coach_selected = {}
for level in coaches_attending:
    coach_final[level] = {}
    for group in group_priority:
        coach_final[level][group] = {}
        temp_keys = list(coach_can_handle_group[level][group])
        commonFunctions.print_random_state("Before Shuffle")
        random.shuffle(temp_keys)
        commonFunctions.print_random_state("After Shuffle")
        max_pref_size = [0,""]
        for teamAppID in temp_keys:
            if teamAppID in coach_selected:
                continue
#                commonFunctions.eprint(f"Already matched {teamAppID}")
            elif coach_can_handle_group[level][group][teamAppID] > max_pref_size[0]:
                max_pref_size = [coach_can_handle_group[level][group][teamAppID],teamAppID]
        # We should have now placed a coach in this group - if we did not get a coach, we look harder
        # Note: I could go back to reshuffle but I have not implemented this at this point"
        if (level == "leads") and (max_pref_size[0] == 0):
            list_of_possible_coaches = []
            for teamAppID in coaches_attending[level]:
                if teamAppID in coach_selected:
                    continue
#                    commonFunctions.eprint(f"Already matched {teamAppID}")
                if coach_group_preference[teamAppID][group] > 0:
                    list_of_possible_coaches.append(teamAppID)
            if len(list_of_possible_coaches) == 0:
                print(f"Unable to find a {level} coach for the {group} group")
            else:
                commonFunctions.print_random_state("Before Choice")
                max_pref_size = [300, random.choice(list_of_possible_coaches)]
                commonFunctions.print_random_state("After Choice")
        # At this point we have a level 2/3 coach for this group, or printed an error
        if max_pref_size[0] > 0:
            coach_selected[max_pref_size[1]] = coaches_attending[level][max_pref_size[1]]
            coach_final[level][group][max_pref_size[1]] = coaches_attending[level][max_pref_size[1]]
            del(coaches_attending[level][max_pref_size[1]])


            
commonFunctions.eprint("Initial matching:")
commonFunctions.epprint(coach_final)

# Now we place the remaining coaches
for level in coaches_attending:
    matched_last_time = True
    while(len(coaches_attending) > 0):
        if matched_last_time:
            for group in group_priority:
                temp_keys = list(coach_can_handle_group[level][group])
                random.shuffle(temp_keys)
                max_pref_size = [0,""]
                for teamAppID in temp_keys:
                    if teamAppID in coach_selected:
                        continue
#                        print(f"Already matched {teamAppID}")
                    elif coach_can_handle_group[level][group][teamAppID] > max_pref_size[0]:
                        max_pref_size = [coach_can_handle_group[level][group][teamAppID],teamAppID]
                # We should have now placed a coach in this group - if we did not get a coach, we look harder
                if max_pref_size[0] > 0:
                    coach_selected[max_pref_size[1]] = coaches_attending[level][max_pref_size[1]]
                    coach_final[level][group][max_pref_size[1]] = coaches_attending[level][max_pref_size[1]]
                    del(coaches_attending[level][max_pref_size[1]])
                    matched_last_time = True
                else:
                    matched_last_time = False
        else:
            break


commonFunctions.eprint("Final Coaches")
commonFunctions.epprint(coach_final)
commonFunctions.eprint("Remaining coaches")
commonFunctions.epprint(coaches_attending)

# save coach data both to file and in the spreadsheet
f = open(f"{args.practice_date}/{args.practice_date}.coaches", "w")

# loop through the column heads to see if we already have a column for this date

column_number = commonFunctions.find_and_clear_column_for_coach_data(coaches_worksheet, coaches_matrix, args.practice_date, True)[0]

    
# Output coach data to the coaches worksheet
count_coaches = {}
coaches_worksheet.update_value((1,column_number), args.practice_date)
coaches_worksheet.cell((1,column_number)).set_text_format('bold', True)
for group in group_names[1:]:
    if group not in group_priority:
        continue
    count_coaches[group] = 0
    for level in ['leads','level1']:
        if group in coach_final[level]:
            for teamAppID in coach_final[level][group]:
                count_coaches[group] += 1
                f.write(f"{teamAppID}\t{group}\n")
                coaches_worksheet.update_value((coach_row_number[teamAppID]+1,column_number), group)
coaches_worksheet.adjust_column_width(column_number)
            


output_matrix = []
header = f"Bolts Cycling Groups ({count_entries} Total signups)"
output_matrix.append([header,""])
print(header)

print( "-----------------------------------------")
output_matrix.append(["",""])

for group in group_names[1:]:
    if group not in group_priority:
        continue
    header = f"{group} ({str(len(groups[group]))} riders, {str(count_coaches[group])} coaches)"
    output_matrix.append([header,""])
    print(header)
    reverse_sort = False
#    if group == 'Coaches':
#        reverse_sort = True
    for level in ['leads','level1']:
        for teamAppID in coach_final[level][group]:
            print("\t"+coach_final[level][group][teamAppID])
            output_matrix.append(["", coach_final[level][group][teamAppID]])
    for name in sorted(groups[group], reverse=reverse_sort):
        print("\t"+name)
        output_matrix.append(["", name])
        
output_matrix.append(["", ""])
if len(unknown) > 0:
    header = "\nNOTE: Could not identifiy "+str(len(unknown))+" TeamApp UserIDs"
    output_matrix.append([header,""])
    print(header)
    for name in unknown:
        print("\t"+name)
        output_matrix.append(["", name])
        
num_rows = len(output_matrix)

# Search for existing version of this spreadsheet - if it does not exist, create a new one
matching_id = ""
drive_list = json.loads(json.dumps(gc.drive.list()))
for ii in range(len(drive_list)):
    if drive_list[ii]["name"] == f"boltsGroups_{args.practice_date}":
        matching_id = drive_list[ii]["id"]
        break
        
if len(matching_id) > 0:
    createdSpreadsheet = gc.open_by_key(matching_id)
else:
    # createdSpreadsheet = gc.create(f"boltsGroups_{args.practice_date}", folder=config.pygsheets_folder_for_practices)
    createdSpreadsheet = gc.create(f"boltsGroups_{args.practice_date}")


# Eventually lock this down????
createdSpreadsheet.share('', role='writer', type='anyone')
output_worksheet = createdSpreadsheet[0]
# In case the sheet already existed, clear it and start over
output_worksheet.clear()
output_worksheet.update_values(crange=f'A1:B{num_rows}', values=output_matrix)

# Format the header
c = output_worksheet.cell("A1")
c.set_text_format("fontSize", 12)
c.set_text_format("bold", True)
gc.drive.move_file(createdSpreadsheet.id,"", new_folder=config.pygsheets_folder_for_practices)


print("\nFind all this information in the google doc:")
print(createdSpreadsheet.url)


