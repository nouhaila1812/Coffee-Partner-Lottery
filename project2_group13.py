import pandas as pd
import datetime
import random

"""
The link to the google form is https://forms.gle/NRS5GVcTEuB94Zuz7
"""

time_format = "%Y-%m-%d %H:%M:%S"

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
    
def make_groups(chosen_size_dict):
     # It would be nice if we considered making groups that minimize repeat meeting
     # Also we need to make the group assignment random which means somehow using the random module

    groups = []

    # goes through each requested group size
    for size in chosen_size_dict:

        people = chosen_size_dict[size]
        random.shuffle(people)
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


def conversation_starter():

    file = open("conversation_starters.txt", "r")

    starters = file.readlines()

    file.close()

    starter = random.choice(starters)

    starter = starter.strip()

    return starter

def create_messages(groups):
    # Get a conversation starter
    starter = conversation_starter()
    
    print("Conversation starter for this round:")
    print(starter)
    print("\n")

    group_number = 1
        
    # Build the text with the names
    for group in groups:
        names_text = ""

        for person in group:
            name = person[1]

            if names_text == "":
                names_text = name
            else:
                names_text = names_text + ", " + name

        message = f"""Hello {names_text},

You have been matched for Coffee Dates!

Your group members are: {names_text}

Conversation starter:
{starter}

Enjoy your coffee date!"""

        print(message)
        print("-------------------------------")

        # Save the message in a text file
        filename = f"group_{group_number}_message.txt"
        with open(filename, "w") as file:
            file.write(message)

        # Increase the group number
        group_number += 1

def main():
    print(f"-------------------------------\nWelcome to Coffee Dates\n-------------------------------")
    print("To access the signup form, please follow this link: https://forms.gle/NRS5GVcTEuB94Zuz7")
    print("Signed up participants are stored in a google sheet that gets read automatically by this program, so no need to download any files")
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
    new_groups = make_groups({str(group_size): eligible_people})

    create_messages(new_groups)

if __name__ == "__main__":
    main()


# Test timeframe
# 2025-03-09
# 2025-03-14
    

