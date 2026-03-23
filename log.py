import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(override=True)

_alert_sent = False
_error_occurred = False


def has_errors():
    return _error_occurred


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
    global _alert_sent, _error_occurred
    _error_occurred = True

    logs_folder = 'Logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    current_date = datetime.date.today().strftime("%Y-%m-%d")
    log_file_name = f"Error_Log_{current_date}.txt"
    log_file_path = os.path.join(logs_folder, log_file_name)

    # Capture before writing so the check and write are in the right order
    is_new_log = not os.path.exists(log_file_path)

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    log_message = f"{current_time} - {event}"

    # Write to file first so the file exists before any email is attempted
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{log_message}\n")

    print(log_message)

    # Send one alert per day (new log file) and at most once per run
    if is_new_log and not _alert_sent:
        try:
            send_alert(f'New error log created\n{event}')
            _alert_sent = True
        except Exception as e:
            print(f"Failed to send alert email: {e}")


def test_smtp_auth():
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.getenv("ALERTUSER")
    password = os.getenv("ALERTPASS")

    print("ALERTUSER:", repr(sender_email))
    print("ALERTPASS length:", len(password) if password else None)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)  # 🔥 prints full SMTP conversation
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, password)
            print("✅ SMTP AUTH SUCCESS")
    except Exception as e:
        print("❌ SMTP AUTH FAILED:", repr(e))
