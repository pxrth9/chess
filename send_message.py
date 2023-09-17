import os
from twilio.rest import Client

# Define your environment variables
account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")
to_whatsapp_no = os.environ.get("to_whatsapp_no")


def send_whatsapp_message(message):
    # Check if required environment variables are set
    if not all([account_sid, auth_token, message, to_whatsapp_no]):
        print("One or more required environment variables are missing.")
        exit(1)

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Send the WhatsApp message
    message = client.messages.create(
        body=message, from_="whatsapp:+14155238886", to=f"whatsapp:{to_whatsapp_no}"
    )
    message_id = message.sid
    print("Message ID:", message_id)
    return message_id
