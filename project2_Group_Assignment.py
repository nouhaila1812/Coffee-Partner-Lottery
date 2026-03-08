import pandas as pd
import datetime
import os
import json

# The link to the google form is ...

all_groups_json = "all_coffee_partners.json"
time_format = "%Y-%m-%d %H:%M:%S"


def load_all_partners():
  # all_partners dictionary is stored in a json file
  # it contains an entry for each participant: key   = participant email / value = list of emails they have been grouped with before
  # it also stores the last time groups were created, so we know which Google Form entries are new
  
    if os.path.exists(all_groups_json):
        with open(all_groups_json) as f:
            all_partners = json.load(f)
    else:
        all_partners = {}

    return all_partners


def google_sheet_to_dict(): 

    chosen_size_dict = {}

    # initializes filter value if it does not exist yet
    if "filter_value" not in all_partners:
        all_partners["filter_value"] = pd.Timestamp("2000-01-01 00:00:00")

    # reads csv from Google Sheet
    df = pd.read_csv( )

    # cleans column names
    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Full Name": "name",
        "Email": "email",
        "How many people do you want in your meeting group?": "group_size"
    })

    # cleans timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.round("min")

    # keeps only new entries and removing duplicates
    df = df[df["timestamp"] > all_partners["filter_value"]]
    df = df.drop_duplicates()

    # groups by requested group size
    grouped = df.groupby(by="group_size")

    # converts grouped data into dictionary
    for group_size, data in grouped:
        chosen_size_dict[str(group_size)] = list(zip(list(data["email"]), list(data["name"])))

    return chosen_size_dict


def make_groups(chosen_size_dict, all_partners):

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

# takes the created groups and updates the all_partners dictionaryso that we know who has already been grouped with whom
def build_all_groups_json(chosen_size_list, all_partners): 
  

    all_partners["filter_value"] = datetime.datetime.now().strftime(time_format)

    for group in chosen_size_list:
        for person in group:
            others = []

            for other_person in group:
                if other_person[0] != person[0]:
                    others.append(other_person[0])

            if person[0] not in all_partners:
                all_partners[person[0]] = []

            all_partners[person[0]] = list(set(all_partners[person[0]] + others))

    with open(all_groups_json, "w") as f:
        json.dump(all_partners, f)


if __name__ == "__main__":
    all_partners = load_all_partners()
    chosen_size_dict = google_sheet_to_dict()
    chosen_size_list = make_groups(chosen_size_dict, all_partners)
    build_all_groups_json(chosen_size_list, all_partners)

    print("Groups created successfully:")
    for group in chosen_size_list:
        print(group)