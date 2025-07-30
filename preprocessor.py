import re
import pandas as pd

def preprocess(data):
    # Updated pattern to correctly extract date-time format
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},?\s\d{1,2}:\d{2}\s?[APap]?[Mm]?)\s-\s'

    messages = re.split(pattern, data)[1:]  # Splitting based on pattern
    dates = re.findall(pattern, data)  # Extracting dates

    if not dates:  # Check if date extraction failed
        print("⚠️ No dates extracted! Check regex pattern.")
    
    # Create DataFrame
    df = pd.DataFrame({'user_message': messages[1::2], 'message_date': dates})

    # Fix date parsing issue
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p', errors='coerce')
    except Exception as e:
        print(f"🚨 Date parsing error: {e}")

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Splitting users and messages correctly
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) == 3:  # Message with a user
            users.append(entry[1].strip())
            messages.append(entry[2].strip())
        else:  # System notification or unknown format
            users.append("group_notification")
            messages.append(entry[0].strip())

    # Ensure lists have the same length as DataFrame
        if len(users) == len(df):
            df['user'] = users
            df['message'] = messages
        else:
            print(f"⚠️ Mismatch: {len(users)} users vs {len(df)} rows in DataFrame!")


    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional time features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Fix period column
    df['period'] = df['hour'].apply(lambda x: f"{x}-{(x+1)%24}")

    return df


