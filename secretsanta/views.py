from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from .models import *


@csrf_exempt
def sms_response(request):
    pprint(request.POST)
    part = None
    if Participant.objects.filter(number=request.POST.get("From", "")).exists():
        part = Participant.objects.filter(number=request.POST.get("From", "")).first()

    Message.objects.create(
        from_number = request.POST.get("From", ""),
        to_number = request.POST.get("To", ""),
        participant = part,
        body = request.POST.get("Body", ""),
        smssid = request.POST.get("MessageSid", ""),
    )

    return HttpResponse("OK")


@staff_member_required
def draw_year(request):
    DrawnName.objects.all().delete()
    current_year = datetime.now().year
    print("Drawing people...")
    for part in Participant.objects.all():
        if DrawnName.objects.filter(
            year=current_year,
            participant=part).exists():
            # Already drawn
            continue

        eligble_users = (
            Participant.objects.all()
            .exclude(pk=part.pk)
            .exclude(excluded__in=part.excluded.all())
            .exclude(
                pk__in=DrawnName.objects.filter(year=current_year).values_list(
                    "recipient", flat=True
                )
            )
        )
        selected_user = eligble_users.order_by('?').first()
        print("Selected: {} has drawn {}".format(
            part,
            selected_user))
        DrawnName.objects.create(
            year=current_year,
            participant=part,
            recipient=selected_user,
        )

    return HttpResponse("Hello, world.")
