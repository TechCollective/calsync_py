import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

smtp_server = "smtp.gmail.com"
smtp_port = 587
user = os.getenv("ALERTUSER")
password = os.getenv("ALERTPASS")

print("User:", user)
print("Password length:", len(password) if password else None)

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.set_debuglevel(1)
    server.starttls()
    server.login(user, password)

print("LOGIN SUCCESS")
