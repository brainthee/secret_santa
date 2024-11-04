# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

recep = "447807874758"

message = client.messages.create(
    from_="+{}".format(os.environ["SENDER"]),
    to="+{}".format(recep),
    body="Hey, my name is Snowflake, the elf!",
)

pprint(message)