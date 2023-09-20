import smtplib
from email.mime.text import MIMEText
import os

FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")


def send_email(
    subject, body, sender=FROM_EMAIL, recipient=TO_EMAIL, password=APP_PASSWORD
):
    # Make sure all the fields are filled in
    if not (sender and recipient and password):
        print("Please fill in all the fields")
        print(sender, recipient, password)
        return

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipient, msg.as_string())
        print("Message sent!")
        return True
    except:
        return False
