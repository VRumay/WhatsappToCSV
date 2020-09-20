
"""

Whatsapp to CSV: Converts any chat file exported from whatsapp as .txt to a .csv file
with the most relevant columns for analysis.
Supports group chats, currently supporting english exports, with a possibility to extend it to spanish

"""

import os
import pandas as pd
import re

chatfile = r"...\chat.txt" 
filename = (os.path.basename(chatfile)).split('.')[0]

# From a .txt file econded as utf8, build a pandas dataframe and use line jumps regex as separator - do not stop at lines that could not be parsed: 
df= pd.read_csv(chatfile, sep = '(\r\n?|\n)+' , header=None,encoding='utf8',engine='python', error_bad_lines=False)

# Set the name of the single column in the dataframe so far:
df.columns = ['datetimesendermessage']

# Split that single column into 2 new columns where the ": " separator is first found, as it marks the colon at the end of the sender name:
datetimesendermessage = df['datetimesendermessage'].str.split(": ", n = 1, expand = True)
df['datetimesender'] = datetimesendermessage[0]
df['message'] = datetimesendermessage[1]

# Metachanges 
titlechanged = 'changed the subject from'
numberchanged = 'changed to +'
adminappointed = " now an admin"
personadded = " added "
imagechanged = "changed this group's icon"
imagedeleted = "deleted this group's icon"
personleft = ' left'
personkicked = ' removed '

def metachanges(change, flag, message):
    if str(df.loc[row, 'datetimesender']).find(change) > 0:
        subjectchange = df.loc[row, 'datetimesender'].split(flag)
        df.loc[row, 'datetimesender'] =  subjectchange[0]
        df.loc[row, 'metachange'] =  (message)
        df.loc[row, 'message'] =  (subjectchange[1])



# Find lines with errors (line jumps as a separator tend to break longer messages on whatsapp chat), what this loop does is iterate over each row and check if the 'datetimesender' column 
# does not have a date formatted

for row in range(1, len(df)):

    if str(df.loc[row, 'datetimesender']).find(' AM - ') == -1 and str(df.loc[row, 'datetimesender']).find(' PM - ') == -1 : 
       df.loc[row, 'message'] = df.loc[row, 'datetimesender'] + str(df.loc[row, 'message'])
       df.loc[row, 'datetimesender'] = df.loc[row-1, 'datetimesender']

# Check for chat title changes 
    metachanges(titlechanged, 'changed the subject from ', 'Conversation Title changed')
    
# Check for person number changes
    metachanges(numberchanged, ' changed to ', 'Number changed to')
 
# Check for admin appointment
    metachanges(adminappointed, "'re now an admin", 'Appointed as Admin')

# Check for new person added
    metachanges(personadded, 'added', 'Added to the conversation')

# Check for group image changed
    metachanges(imagechanged, "changed this group's icon", 'Conversation Image was changed')

# Check for group image deleted
    metachanges(imagedeleted, "deleted this group's icon",'Conversation Image was deleted')
    
# Check for leaving person
    metachanges(personleft, ' left', 'Left the Conversation')

# Check for removed person
    metachanges(personkicked, ' removed ', 'Kicked from the Conversation')

# Datetime & Sender column

datetimesender = df['datetimesender'].str.split(" - ", n = 1, expand = True)
df['datetime'] = datetimesender[0]
df['sender'] = datetimesender[1].replace(" deleted this group's icon",'') 


# Split 'datetime' column into Date & Time Columns

datetimesender = df['datetime'].str.split(", ", n = 1, expand = True)
df['date'] = datetimesender[0]
df['time'] = datetimesender[1]

# Extract emojis and save to 'emojis' column

df['emojis'] = df['message'][df['message'].str.contains(u"[^\U00000000-\U0000d7ff\U0000e000-\U0000ffff]", flags=re.UNICODE, na=False)] # replace match with contains
#df['emojis'] = df['emojis'].replace(f"[\s\w\d\\().:«»~-]","", regex=True, inplace=True) # Won't delete punctuation, but it would be more efficient. 

abc123 = [' ','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','0','1','2','3','4','5','6', '7', '8', '9','!',',','.','?','¿','ñ','é','ó','á','ú','í','%','(',')','*','_','-','"','@','/',';',':','¡','=','+','’','[',']','>','“','”','&','#','【','﻿','ｗ','ｖ','】']
for i in abc123:
    df['emojis'] = df['emojis'].str.replace(i, "", regex=False)
    df['emojis'] = df['emojis'].str.replace(i.upper(), "", regex=False)

# Keep only relevant columns
df = df[['date','time','sender','message','metachange','emojis']]

# Save excel file in cwd
df.to_csv(f'{filename}.csv',encoding='utf-8-sig',index=False)


