import smtplib
from email.mime.text import MIMEText
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")


def send_email(
    subject, body, sender=FROM_EMAIL, recipient=TO_EMAIL, password=APP_PASSWORD
):
    # Make sure all the fields are filled in
    if not (sender and recipient and password):
        logging.error("Please fill in all the fields")
        logging.error(f"Sender: {sender}, Recipient: {recipient}, Password: {password}")
        return

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipient, msg.as_string())
        logging.info("Message sent!")
        return True
    except Exception as e:
        logging.error(str(e))
        return False
