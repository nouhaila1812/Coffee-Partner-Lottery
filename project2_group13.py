import pandas as pd
import datetime
import os
import json
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

def google_sheet_to_dict():
    """
    Google form is linked to a google sheet which can be read by pandas csv reader.
    The titles are cleaned for easy typing, times are rounded to nearest minute and duplicates are dropped. Dataframe is grouped by the amount of people they want to be in a group with.
    Returns dictionary whos keys are desired group sizes, and values are lists of corresponding emails that want that group size.
    """
    chosen_size_dict = {}

    # initializes filter value
    if not "filter_value" in all_past_partners:
        all_past_partners["filter_value"] = pd.Timestamp("2000-01-01 00:00:00")
    
    # creates and cleans DataFrame, remove duplicates and make column names easier
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/15pMlh8APUGehoKDdlcW-B_BQHElrQbRLL63hRNFInEc/export?format=csv")
    df = df.rename(columns = {"Timestamp": "timestamp", "Full Name": "name", "Email": "email", "How many people do you want in your meeting group?": "group_size"})
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.round("min")
    df = df[df["timestamp"] > all_past_partners["filter_value"]].drop_duplicates().groupby(by="group_size")

    # turns DataFrame into dictionary
    for group_size, data in df:
        chosen_size_dict[str(group_size)] = list(zip(list(data["email"]), list(data["name"])))
    return(chosen_size_dict) # The dictionaries structure is chosen_size_dict[desired group size] = [(personA email, personA name), (personB email, personB name)]

def make_groups(chosen_size_dict, all_past_partners):

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
    all_past_partners["filter_value"] = datetime.datetime.now().strftime(time_format)
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

if __name__ == "__main__":
    all_past_partners = load_all_partners()
    chosen_size_dict = google_sheet_to_dict()
    new_groups = make_groups(chosen_size_dict, all_past_partners)
    build_all_past_partners_json(new_groups, all_past_partners)

    print("Groups created successfully:")
    for group in new_groups:
        print(group)

