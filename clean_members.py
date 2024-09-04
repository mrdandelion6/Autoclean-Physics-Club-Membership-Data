import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import os

KEY_SECRET_PATH = 'key_secret.json'
PLOT_OUTPUT_PATH = '../plots/'
PLOT_TITLE = 'Membership Distribution'
FILE_NAME = PLOT_TITLE.lower().replace(' ', '_') + '.png' # snake case

# change directory to script location. this is for when we save some output visualizations
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory) 

# use creds to create a client to interact with the Google Drive API
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_SECRET_PATH, scope)
client = gspread.authorize(creds) # authorize our client with the credentials

# open our sheets
sheet1 = client.open('member_list').sheet1
sheet2 = client.open('member_list').get_worksheet(1)

# access data from the first sheet
data = pd.DataFrame(sheet1.get_all_records())
data.loc[data["Do you attend the University of Toronto Mississauga ?"] == "Yes", "What university do you attend ?"] = "UTM"
data["Email"] = data["Email"] + data["UofT Email"]
pd.set_option('display.max_rows', None)

# filter out individuals eligible for membership
is_member = (data['Level of Study'] == 'Undergraduate') & (data['Do you attend the University of Toronto Mississauga ?'] == 'Yes')
# we want uoft attendees who are undergraduates

members = data[is_member]
associate_members = data[~is_member]
# we drop all the empty columns

# we want to reorder columns based on sheet2 in the googlesheet
members_cols = ["Timestamp", "First Name", "Last Name", "UofT Email", "Student Number", "UTORid (optional)", "Discord Username (optional)"]
associate_cols = ["Timestamp", "First Name", "Last Name", "Email", "Student Number", "What university do you attend ?", "Level of Study", "Discord Username (optional)"]

# lets also rename some columns
rename_dict = {
    "Timestamp": "Time",
    "Student Number": "Student #",
    "Discord Username (optional)": "Discord",
    "Level of Study": "Study Level",
    "What university do you attend ?" : "University",
    "UTORid (optional)": "UTORid"
}

# apply our transformations
members = members[members_cols].rename(columns=rename_dict)
associate_members = associate_members[associate_cols].rename(columns=rename_dict)

# now lets make a new dataframe to store all members data in
all_members = pd.DataFrame(columns=["Time", "First Name", "Last Name", "Email", "Student #", "University", "UTORid", "Study Level", "Discord"])

# we have to combine the two members and associate_members dataframes carefully.
all_members["Time"] = pd.concat([members["Time"], associate_members["Time"]], ignore_index=True)
all_members["First Name"] = pd.concat([members["First Name"], associate_members["First Name"]], ignore_index=True)
all_members["Last Name"] = pd.concat([members["Last Name"], associate_members["Last Name"]], ignore_index=True)
all_members["Email"] = pd.concat([members["UofT Email"], associate_members["Email"]], ignore_index=True)
all_members["Student #"] = pd.concat([members["Student #"], associate_members["Student #"]], ignore_index=True)
all_members["University"] = pd.concat([pd.Series(["UTM" for _ in range(len(members))]), associate_members["University"]], ignore_index=True)
all_members["UTORid"] = pd.concat([members["UTORid"], pd.Series(["" for _ in range(len(associate_members))])], ignore_index=True)
all_members["Study Level"] = pd.concat([pd.Series(["Undergraduate" for _ in range(len(members))]), associate_members["Study Level"]], ignore_index=True)
all_members["Discord"] = pd.concat([members["Discord"], associate_members["Discord"]], ignore_index=True)

# prints for sanity checks
# print(members)
# print(associate_members)
# print(all_members)

# now let's update sheet2 on our google sheet. need to turn the dataframes into lists first
members = members.values.tolist()
associate_members = associate_members.values.tolist()
all_members = all_members.values.tolist()

# before printing to the sheet, we need to clear the existing data
start_row = 9  # starting from row 9

# clean base members
range_to_clear = f"B{start_row}:I"  
sheet2.batch_clear([range_to_clear]) 

# clean associate members
range_to_clear = f"K{start_row}:S"
sheet2.batch_clear([range_to_clear])

# clean all members
range_to_clear = f"U{start_row}:AD"
sheet2.batch_clear([range_to_clear])

# now update the sheet with the new data
sheet2.update(range_name='C9', values=members)
sheet2.update(range_name='B9', values=[[str(len(members))]]) # also update counts
sheet2.update(range_name='L9', values=associate_members)
sheet2.update(range_name='K9', values=[[str(len(associate_members))]])
sheet2.update(range_name='V9', values=all_members)
sheet2.update(range_name='U9', values=[[str(len(all_members))]])


# save some visualizations
sizes = [len(members), len(associate_members)]
labels = ['Members', 'Associate Members']
plt.figure(figsize=(8, 8)) 
plt.pie(sizes, labels=labels, autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100.*sum(sizes))})', startangle=140)
plt.title(PLOT_TITLE)
plt.savefig(PLOT_OUTPUT_PATH + FILE_NAME, dpi=300, bbox_inches='tight')

print("script ran successfully")