import pandas as pd
import os

all_groups_csv = "all_coffee_partners.csv"

def google_sheet_to_dict():
    """
    Google form is linked to a google sheet which can be read by pandas csv reader.
    The titles are cleaned for easy typing, times are rounded to nearest minute and duplicates are dropped. Dataframe is grouped by the amount of people they want to be in a group with.
    Returns dictionary whos keys are desired group sizes, and values are lists of corresponding emails that want that group size.
    """
    chosen_size_dict = {}
    if os.path.exists(all_groups_csv):
        filter_value = pd.to_datetime(pd.read_csv(all_groups_csv, col="creation_time")).max()
    else:
        filter_value = "2000-01-01 00:00:00"
        
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/15pMlh8APUGehoKDdlcW-B_BQHElrQbRLL63hRNFInEc/export?format=csv")
    df = df.rename(columns = {"Timestamp": "timestamp", "Full Name": "name", "Email": "email", "How many people do you want in your meeting group?": "group_size"})
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.round("min")
    df = df[df["timestamp"] > filter_value].drop_duplicates().groupby(by="group_size")
    for group_size, data in df:
        chosen_size_dict[str(group_size)] = list(data["email"])
    return(chosen_size_dict)

def make_groups():
    pass

if __name__ == "__main__":
    chosen_size_dict = google_sheet_to_dict()
    print(chosen_size_dict["3"])