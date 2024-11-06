#!/opt/anaconda3/bin/python
# %% [markdown]
# ## Automated Email Notification Setup
# 
# ### Goal: 
# The script is coded to send an email notification if a used Honda Pilot car with Price < 35000, Miles < 30000 and State = TX is found.

# %% [markdown]
# ### Step 0: Import the packages

# %%
#!/opt/anaconda3/bin/python

import os
import pyodbc                           # To connect SQL and Python
import smtplib                          # For email
from email.mime.text import MIMEText    # Email message in text
import logging                          # Store the update info as logs in text file
from datetime import datetime           # Date and time manipulation

# %% [markdown]
# ### Step 1: Define directories, file paths
# We set up two log files and ensure the directories and files we need are in place.
# 
# Purpose:
# 1. A log file for recording the timestamp each time the code is executed and checking if any new VINs are found.
# 
# 2. A file to store previous VINs, allowing us to compare existing VINs in the database with new ones, so we only log or process new, unique VINs.

# %%
# Define path to create the log files
directory_path = 'Your/directory/path/here'
log_file_path = os.path.join(directory_path, 'vin_check.log')       # To log time, and if new VINs were found
vin_file_path = os.path.join(directory_path, 'previous_vins.txt')   # File to store previous VINs, to cross check with any new entries

# Creates the directory if it already doesn't exist
os.makedirs(directory_path, exist_ok=True)

# Sets up the log, to track the time of code execution, new VINs.
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# %% [markdown]
# ### Step 2: Setup Email Notifications

# %%
# Starting a function to send email notification, if a certain criteria of a car is made. 
# Email Address and Password is for SMTP authentication.
def send_email(new_entries):
    EMAIL_ADDRESS = "YourEmailAddressHere@gmx.com"
    EMAIL_PASSWORD = "YourEmailAddressHere"
    RECIPIENT_EMAIL = "ReceipientEmailAddressHere"

    subject = "New VIN Entries Found in Honda Pilot Table"
    body = "New VIN Entries:\n" + "\n".join([f"Year: {entry.Year}, Model: {entry.Model}, Price: {entry.Price}, Miles: {entry.Miles}, URL: {entry.URL}, VIN: {entry.VIN}" for entry in new_entries])

    msg = MIMEText(body) # MIMEText writes the email, with subject, sender, recipients.
    msg['Subject'] = subject 
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL

    try: # Creates connection with gmx's SMTP server, login details for authentication.
        with smtplib.SMTP_SSL('smtp.gmx.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info("Email sent successfully.")
        return True
    except Exception as e:
        logging.error(f"Error sending email: {e}") # For success or error logging. 
        return False


# %% [markdown]
# ### Step 3: Query data from SQL database

# %%
# In this step, we connect to the SQL Server, look into the database and retreive required information.
# Using Docker as Data Container in my case, using SQL on Azure Data Studio.

def check_new_vin(previous_vin_set):
    connection = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=DatabaseNameHere;'
        'UID=SA;'
        'PWD=YourPasswordHere;'
        'Encrypt=yes;'
        'TrustServerCertificate=yes;'
        'Connection Timeout=30;'
    )

    cursor = connection.cursor()  
    # Writing the SQL query here to retreive the car that is desired.
    query = """
        SELECT Year, Model, Price, Miles, VIN, URL 
        FROM honda_pilot 
        WHERE Price < 35000 AND Miles < 30000
        AND State = 'TX'
    """
    cursor.execute(query)
    new_entries = cursor.fetchall()  # Fetch all records that meet the conditions
    
    # Creates a set for new VIN which meets above conditions.
    new_vin_set = {row.VIN for row in new_entries}
    # Check for new VINs.
    new_vins = new_vin_set - previous_vin_set  

    # Every time the code is run, a log with date, time is made. 
    logging.info(f"Code run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if new_vins:
        # Log the unique new VIN entries
        filtered_new_entries = [row for row in new_entries if row.VIN in new_vins]
        logging.info(f"New unique VIN entries found: {len(filtered_new_entries)}")
        for entry in filtered_new_entries:
            logging.info(f"New VIN: {entry.VIN}, Year: {entry.Year}, Model: {entry.Model}, Price: {entry.Price}, Miles: {entry.Miles}, URL: {entry.URL}")

        # Send email notification if a new VIN is identified.
        email_sent = send_email(filtered_new_entries)
        if email_sent:
            logging.info("Email sent successfully with new VIN entries.")
        else:
            logging.info("Email was not sent due to an error.")
    # For no new entries:
    else:
        logging.info("No new unique VINs detected.")

    cursor.close()
    connection.close() # Closes the SQL server connection. 

    return new_vin_set  
# Returns the new VIN set for next comparison.
# Closing the function

# %% [markdown]
# ### Step 4: Cross-Checking for new VIN & Logging
# The above queried data is retreived and checked with the previously queried data, where unique VINs are stored in a text file.
# If a new VIN is identified, an email notification is sent.

# %%
# Loading the previous VINs from the file
if os.path.exists(vin_file_path):
    with open(vin_file_path, 'r') as f:
        lines = f.readlines()
        if lines:
            previous_vin_set = set(line.strip() for line in lines)  # This retreives the above recorded VIN for comparison.
        else:
            previous_vin_set = set()  
else:
    previous_vin_set = set()  # Defaults to empty set if the file does not exist

# Run the function
previous_vin_set = check_new_vin(previous_vin_set)

# %%
# If new VINs are recorded, this saves it to a file. This will be reviewed by the future queries to identify new VIN entry.
with open(vin_file_path, 'w') as f:
    for vin in previous_vin_set:
        f.write(f"{vin}\n")

# Ensure the logging is flushed to the log file
logging.shutdown()


