import os
from twilio.rest import Client
from django.conf import settings
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

    msg = Message.objects.create(
        from_number=settings.TWILIO_SENDER,
        to_number=participant.number,
        participant=participant,
        body=content,
    )
    return message
