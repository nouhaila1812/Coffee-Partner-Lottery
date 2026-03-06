import pandas as pd


def download_csv():
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/15pMlh8APUGehoKDdlcW-B_BQHElrQbRLL63hRNFInEc/export?format=csv")
    return df

if __name__ == "__main__":
    print(download_csv())