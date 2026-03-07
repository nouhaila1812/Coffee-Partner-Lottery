import pandas as pd

def google_sheet_to_dataframe():
    """
    Google form is linked to a google sheet which can be read by pandas csv reader.
    The titles are cleaned for easy typing, times are rounded to nearest minute and duplicates are dropped. Dataframe is grouped by the amount of people they want to be in a group with.
    """
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/15pMlh8APUGehoKDdlcW-B_BQHElrQbRLL63hRNFInEc/export?format=csv")
    df = df.rename(columns = {"Timestamp": "timestamp", "Full Name": "name", "Email": "email", "How many people do you want in your meeting group?": "group_size"})
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = df["timestamp"].dt.round("min")
    df = df.drop_duplicates()
    df = df.groupby(by="group_size")
    return df

if __name__ == "__main__":
    print(google_sheet_to_dataframe().get_group(2))
    print(google_sheet_to_dataframe().get_group(3))
    print(google_sheet_to_dataframe().get_group(4))