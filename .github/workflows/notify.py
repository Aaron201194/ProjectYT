import os
import json
import gspread
import smtplib
from email.message import EmailMessage

# --- 1. Load Environment Variables ---
google_creds_json = os.environ.get('GOOGLE_CREDENTIALS')
sheet_id = os.environ.get('SHEET_ID')
smtp_user = os.environ.get('SMTP_USER')
smtp_password = os.environ.get('SMTP_PASSWORD')
release_name = os.environ.get('RELEASE_NAME', 'New Release')
release_body = os.environ.get('RELEASE_BODY', 'A new release is available.')

# --- 2. Fetch Emails from Google Sheets ---
# Authenticate using the service account JSON
creds_dict = json.loads(google_creds_json)
gc = gspread.service_account_from_dict(creds_dict)

# Open the sheet by its ID (found in the URL: docs.google.com/spreadsheets/d/<SHEET_ID>/edit)
sh = gc.open_by_key(sheet_id)
worksheet = sh.sheet1 

# Get all data. This assumes your Form creates a column exactly titled "Email Address"
# Change 'Email Address' below if your Google Form question is worded differently.
records = worksheet.get_all_records()
email_addresses = [row['Email Address'] for row in records if row.get('Email Address')]

# Remove duplicates just in case someone submitted the form twice
unique_emails = list(set(email_addresses))

if not unique_emails:
    print("No email addresses found in the sheet. Exiting.")
    exit()

print(f"Found {len(unique_emails)} subscribers. Preparing to send...")

# --- 3. Send the Emails ---
try:
    # Connect to Gmail's SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)

    for email in unique_emails:
        msg = EmailMessage()
        msg.set_content(f"Hello!\n\nA new release '{release_name}' has been published.\n\nRelease Notes:\n{release_body}")
        
        msg['Subject'] = f"New GitHub Release: {release_name}"
        msg['From'] = smtp_user
        msg['To'] = email

        server.send_message(msg)
        print(f"Sent to {email}")

    server.quit()
    print("All notifications sent successfully.")

except Exception as e:
    print(f"Error sending emails: {e}")
    exit(1)