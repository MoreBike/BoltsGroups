import sys
import random
from pprint import pprint
##############################################################
# Subroutines
##############################################################

enable_printing_random_state = False
number_of_columns_not_to_be_overwritten = 20


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
def epprint(*args):
    pprint(*args, sys.stderr)
def print_random_state(my_location):
    random_diffs = ""
    new_random_state = random.getstate()
    if print_random_state.saved_random_state[0] != new_random_state[0]:
        random_diffs += f"\tDiff at [0] - {print_random_state.saved_random_state[0]} -> {new_random_state[0]}\n"
    for ii in range(len(new_random_state[1])):
        if print_random_state.saved_random_state[1][ii] != new_random_state[1][ii]:
            random_diffs += f"\tDiff at [1][{ii}] - {print_random_state.saved_random_state[1][ii]} -> {new_random_state[1][ii]}\n"
    if len(random_diffs) == 0:
        random_diffs = "No Change"
    if enable_printing_random_state:
        print(f"{my_location} - ", random_diffs)
    print_random_state.saved_random_state = new_random_state
    
def find_and_clear_column_for_coach_data(coaches_worksheet, coaches_matrix, practice_date, skip_erase):
    column_number = 1
    date_found = False
    for header in coaches_matrix[0]:
        if header == practice_date:
            date_found = True
            break
        column_number += 1

    # When we get here, either the column_number is the one with data
    # from this day, or one more than the end of the list.  Remember,
    # coaches_matrix[0] is indexed from zero but when using
    # coaches_worksheet, that is indexed from 1, which is what
    # column_number is tracking
    if date_found:
        # erase everything in the columns
        if not skip_erase:
            coaches_worksheet.clear((1,column_number), (coaches_worksheet.rows,column_number), "*")
        return(column_number, date_found)

    # We get here if the date wasn't found and column_number is 1 past the end.  
    # Work back to first empty spot.
    column_number -= 1 # coaches_worksheet index
    add_column = True
    while(column_number > number_of_columns_not_to_be_overwritten):
        if len(coaches_matrix[0][column_number-1]) == 0:
            column_number -= 1
            add_column = False
        else:
            break
        
    # If we didn't find a blank one, create it 
    if add_column:
        coaches_worksheet.add_cols(1)
    return(column_number+1, date_found)
    

def find_and_get_column_for_coach_data(coaches_matrix, practice_date):
    column_number = 20
    date_found = False
    coach_saved_group = {}
    coach_row_number = {}
    for header in coaches_matrix[0][column_number:]:
        if header == practice_date:
            date_found = True
            break
        column_number += 1

    if not date_found:
        eprint(f"WARNING - Could not find {practice_date} - figure out how to delete it")
        # epprint(coaches_matrix)
        # eprint("------------------")
        return(coach_saved_group, coach_row_number, column_number)
        
    print(f"Working {practice_date}")
    for my_index, row in enumerate(coaches_matrix[1:]):
        coach_name = f"{row[0]}, {row[1]}"
        coach_row_number[coach_name] = my_index+1
        if len(row[column_number])>0:
            coach_saved_group[coach_name] = f"{row[column_number]}"
            # print(f"{coach_name} - {row[column_number]}")
    return(coach_saved_group, coach_row_number, column_number)
    

    
