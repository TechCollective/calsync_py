import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def send_alert(body):
    # Email configuration for Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.getenv("ALERTUSER")
    receiver_email = os.getenv("ALERTRECIPIENT")
    password = os.getenv("ALERTPASS")

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'CALSYNC ALERT'

    # Email body
    body = f'CALSYNC ERROR\n\n{body}.'
    message.attach(MIMEText(body, 'plain'))

    # Establish a connection to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Encrypt the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def log_event(event):
    # Create the 'Logs' folder if it doesn't exist
    logs_folder = 'Logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Get the current date in the format "YYYY-MM-DD"
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Create the log file name
    log_file_name = f"Event_Log_{current_date}.txt"

    # Create the full file path
    log_file_path = os.path.join(logs_folder, log_file_name)

    # Get the current time in the format "HH:MM:SS"
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Create the log message with timestamp
    log_message = f"{current_time} - {event}"

    # Write the log message to the log file
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{log_message}\n")

    print(log_message)


def log_error(event):
    # Create the 'Logs' folder if it doesn't exist
    logs_folder = 'Logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Get the current date in the format "YYYY-MM-DD"
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Create the log file name
    log_file_name = f"Error_Log_{current_date}.txt"

    # Create the full file path
    log_file_path = os.path.join(logs_folder, log_file_name)

    # Send email alert when error log file is created
    if os.path.exists(log_file_path) == False:
        send_alert(f'New error log created\n{event}')

    # Get the current time in the format "HH:MM:SS"
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Create the log message with timestamp
    log_message = f"{current_time} - {event}"

    # Write the log message to the log file
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{log_message}\n")

    print(log_message)
