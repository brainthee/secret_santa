import os
from twilio.rest import Client
from django.conf import settings
from pprint import pprint
from .models import *


def send_sms(
    participant=None,
    content="",
):
    if not participant or not content:
        print("Missing bits")
        return False

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_="+{}".format(settings.TWILIO_SENDER),
        to="+{}".format(participant.number),
        body=content,
    )
    pprint(message)
    return message
