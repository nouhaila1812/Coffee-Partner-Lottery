import pandas as pd
import datetime
import os
import json
import random

"""
The link to the google form is https://forms.gle/NRS5GVcTEuB94Zuz7
"""
all_met_people_dict = "all_coffee_partners.json"
time_format = "%Y-%m-%d %H:%M:%S"

def load_all_partners():
    """
    The all_past_partners dictionary is stored in a json file, it contains an entry for each participant
    the participants email is their key, and the peoples emails theyve been grouped with before are
    the values (in a list). This dictionary also saves the last time groups were created so we know
    which entries are new and which are old.
    """
    if os.path.exists(all_met_people_dict):
        with open(all_met_people_dict) as f:
            all_past_partners = json.load(f)
    else:
        all_past_partners = {}
    return all_past_partners

def google_sheet_to_dict(time_frame):
    """
    Google form is linked to a google sheet which can be read by pandas csv reader.
    The titles are cleaned for easy typing, times are rounded to nearest minute and duplicates are dropped. 
    Returns list of current participants emails.
    """
    
    # creates and cleans DataFrame, remove duplicates and make column names easier
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/15pMlh8APUGehoKDdlcW-B_BQHElrQbRLL63hRNFInEc/export?format=csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.round("min")
    df = df[(df["Timestamp"] <= time_frame[1]) & (df["Timestamp"] >= time_frame[0])].drop_duplicates()

    # turns DataFrame into list of emails and names
    return list(zip(list(df["Email"]), list(df["Full Name"])))
    
def make_groups(chosen_size_dict, all_past_partners):
     # It would be nice if we considered making groups that minimize repeat meeting
     # Also we need to make the group assignment random which means somehow using the random module

    groups = []

    # goes through each requested group size
    for size in chosen_size_dict:

        people = chosen_size_dict[size]
        size = int(size)

        i = 0

        # creates groups until all people in this size category are processed
        while i < len(people):

            group = []
            j = 0

            # fills one group up to the requested size
            while j < size and i < len(people):
                person = people[i]
                group.append(person)
                i = i + 1
                j = j + 1

            # if the group is full, adds it directly
            if len(group) == size:
                groups.append(group)

            # if there are leftover people, adds them to existing groups
            else:
                if len(groups) > 0:
                    k = 0
                    while k < len(group):
                        groups[k % len(groups)].append(group[k])
                        k = k + 1
                else:
                    groups.append(group)

    return groups


def build_all_past_partners_json(new_groups, all_past_partners):
    """
    takes the made groups and adds them to the dictionary to see who has been in a group with who
    """

    for group in new_groups:
        
        for person in group:
            others = []

            for people in group:
                if people[0] != person[0]:
                    others.append(people[0])
            
            if person[0] not in all_past_partners:
                all_past_partners[person[0]] = []

            all_past_partners[person[0]] = list(set(all_past_partners[person[0]] + others))
    
    with open(all_met_people_dict, "w") as f:
        json.dump(all_past_partners, f)

def create_messages(new_groups):
    pass


def main():
    all_past_partners = load_all_partners()

    while True:
        use_timeframe = input("Would you like to use participant entries from a certain timeframe (y/n)? ")
        if use_timeframe == "y":
            earliest_date = input("What is the earliest signup date you want to use data from (format: YYYY-MM-DD)? ")
            latest_date = input("What is the latest signup date you want to use data from (format: YYYY-MM-DD)? ")
            try:
                time_frame = [pd.Timestamp(earliest_date), pd.Timestamp(latest_date) + datetime.timedelta(days=1)]
                break
            except Exception as e:
                print(f"There was an error with your chosen timeframe: {e}")
                print("Please try again")
                continue
        elif use_timeframe == "n":
            print("Using all signups")
            time_frame = [pd.Timestamp("2000-01-01"), pd.Timestamp("2100-01-01")]
            break
        else:
            print("Invalid input, please try again")
        
    eligible_people = google_sheet_to_dict(time_frame)
    if len(eligible_people) < 2:
        print("Fewer than 2 people signed up in this timeframe, sadly no groups can be formed.")
        return None
    
    while True:
        group_size = int(input(f"There are {len(eligible_people)} people signed up. How many people should be in each group? "))
        if group_size > len(eligible_people):
            print("Group size must be less than, or equal to, the number of signed up participants.")
        elif group_size < 2:
            print("Groups must be comprised of 2 or more people")
        else:
            break
    new_groups = make_groups({str(group_size): eligible_people}, all_past_partners)

    build_all_past_partners_json(new_groups, all_past_partners)


if __name__ == "__main__":
    main()
# Test timeframe
# 2025-03-09
# 2025-03-14
    

