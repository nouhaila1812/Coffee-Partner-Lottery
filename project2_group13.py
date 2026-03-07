import pandas as pd
import datetime
import os
"""
The link to the google form is https://forms.gle/NRS5GVcTEuB94Zuz7
"""
all_groups_csv = "all_coffee_partners.csv"
time_format = "%Y-%m-%d %H:%M:%S"

def google_sheet_to_dict():
    """
    Google form is linked to a google sheet which can be read by pandas csv reader.
    The titles are cleaned for easy typing, times are rounded to nearest minute and duplicates are dropped. Dataframe is grouped by the amount of people they want to be in a group with.
    Returns dictionary whos keys are desired group sizes, and values are lists of corresponding emails that want that group size.
    """
    chosen_size_dict = {}

    # Find last time meetings happend
    if os.path.exists(all_groups_csv):
        filter_value = pd.to_datetime(pd.read_csv(all_groups_csv, usecols=["creation_time"])["creation_time"], format=time_format).max()
    else:
        filter_value = pd.Timestamp("2000-01-01 00:00:00")
    
    # creates and cleans DataFrame, remove duplicates and make column names easier
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/15pMlh8APUGehoKDdlcW-B_BQHElrQbRLL63hRNFInEc/export?format=csv")
    df = df.rename(columns = {"Timestamp": "timestamp", "Full Name": "name", "Email": "email", "How many people do you want in your meeting group?": "group_size"})
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.round("min")
    df = df[df["timestamp"] > filter_value].drop_duplicates().groupby(by="group_size")

    # turns DataFrame into dictionary
    for group_size, data in df:
        chosen_size_dict[str(group_size)] = list(zip(list(data["email"]), list(data["name"])))
    return(chosen_size_dict) # The dictionaries structure is chosen_size_dict[desired group size] = [(personA email, personA name), (personB email, personB name)]

def make_groups(chosen_size_dict):
    """
    needs to be built, please return the groups in format [[personA, personB, personC], [personD, personE]]
    each sublist being a group. 
    """
    chosen_size_list = []
    for key in chosen_size_dict:
        chosen_size_list.append(chosen_size_dict[key])
    return chosen_size_list

def build_all_groups_csv(chosen_size_list):
    """
    takes the made groups and adds them to the CSV with all groups ever made
    """
    now = datetime.datetime.now().strftime(time_format)
    df = pd.DataFrame({"creation_time": [now]*len(chosen_size_list), "groups": chosen_size_list})
    if os.path.exists(all_groups_csv):
        df.to_csv(all_groups_csv, mode="a", header=False, index=False)
    else:
        df.to_csv(all_groups_csv, mode="w", header=True, index=False)
    

if __name__ == "__main__":
    chosen_size_dict = google_sheet_to_dict()
    chosen_size_list = make_groups(chosen_size_dict)
    res = build_all_groups_csv(chosen_size_list)
    print(res)
