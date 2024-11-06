from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pprint import pprint
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.utils import timezone
from .models import *
import time
from .utils import send_sms


@csrf_exempt
def sms_response(request):
    current_year = timezone.datetime.now().year
    part = None
    if Participant.objects.filter(number=request.POST.get("From", "")).exists():
        part = Participant.objects.filter(number=request.POST.get("From", "")).first()

    msg = Message.objects.create(
        from_number=request.POST.get("From", ""),
        to_number=request.POST.get("To", ""),
        participant=part,
        body=request.POST.get("Body", ""),
        smssid=request.POST.get("MessageSid", ""),
    )

    if not part:
        # Unknown user!
        return HttpResponse("WHORU")

    # Legit user...
    current_wishlist,_ = WishList.objects.get_or_create(
        participant=part, year=current_year
    )
    if current_wishlist.is_complete:
        # if msg.body.lower() == "yes":
        #     send_sms(
        #         participant=part,
        #         content="Okay! Please share 3 things you'd love to receive (no prices or hints, just fun surprises!)".format(
        #             part.name,
        #         ),
        #     )
        #     current_wishlist.is_complete = False
        #     current_wishlist.save()
        # else:
        #     send_sms(
        #         participant=part,
        #         content="Hmm, sorry {}! As a small but special elf, I'm not sure I understood your message. Do you want to update your wishlist? Simply say yes if you do - that would help my North Pole brain!".format(
        #             part.name,
        #         ),
        #     )

        send_sms(
            participant=part,
            content="Hmm, sorry {}! As a small but special elf, I'm not sure I understood your message. I've got your wishlist and you should know who your recipient is.".format(
                part.name,
            ),
        )
    else:
        if msg.body.lower() == "yes":
            send_sms(
                participant=part,
                content="Amazing! I've got: \"{}\". I'll pass that on to your Secret Santa 🎄 :)".format(
                    current_wishlist.content,
                    part.name,
                ),
            )
            current_wishlist.is_complete = True
            current_wishlist.save()
        else:
            if current_wishlist.content:
                current_wishlist.content = str(current_wishlist.content) + "\n" + msg.body
            else:
                current_wishlist.content = msg.body
            current_wishlist.save()
            send_sms(
                participant=part,
                content="Got it. Is that everything? (Please reply \"yes\" or tell me more)".format(
                    part.name,
                ),
            )

    return HttpResponse("OK")


@staff_member_required
def clear(request):
    DrawnName.objects.all().delete()
    WishList.objects.all().delete()

## MAKE CRON JOB HITTING /DRAW EVERY 10 MINUTES


@staff_member_required
def draw_year(request):
    # DrawnName.objects.all().delete()
    # WishList.objects.all().delete()
    current_year = timezone.datetime.now().year
    for part in Participant.objects.all():
        current_wishlist,_ = WishList.objects.get_or_create(
            participant=part, year=current_year
        )

        if DrawnName.objects.filter(year=current_year, participant=part).exists():
            # Already drawn - see if we need to do any bits
            draw = DrawnName.objects.get(year=current_year, participant=part)
            r_wishlist,_ = WishList.objects.get_or_create(
                participant=draw.recipient, year=current_year
            )

            if not draw.intro_sent:
                # Send intro text!
                send_sms(
                    participant=part,
                    content="Hey {name}! I'm Snowflake ❄, your family's {current_year} Secret Santa Helper. You'll be selected one person to gift on {draw_date}, your budget will be £{budget}. Watch this space! 🎄".format(
                        name=part.name,
                        current_year=current_year,
                        draw_date=settings.DRAW_DATE,
                        budget=settings.DRAW_BUDGET,
                    ),
                )
                draw.intro_sent = True

            elif not draw.drawn_1_sent:
                # Send draw info
                send_sms(
                    participant=part,
                    content="🥁🥁 Drum roll 🥁🥁 You have been selected...",
                )
                draw.drawn_1_sent = True
            elif not draw.drawn_2_sent:
                send_sms(
                    participant=part,
                    content="🎁 {} 🎁".format(
                        draw.recipient.name.upper(),
                    ),
                )
                draw.drawn_2_sent = True
            elif not draw.drawn_3_sent:
                send_sms(
                    participant=part,
                    content="I'll send you their wishlist once I have it. Remember, no telling! Get ready to surprise them on {}. Your budget is £{}. Love and sparkles - Snowflake the Elf ✨🎄✨".format(
                        settings.DRAW_DATE,
                        settings.DRAW_BUDGET,
                    ),
                )
                draw.drawn_3_sent = True

            elif not current_wishlist.is_complete:
                if not current_wishlist.reminder_sent:
                    # No reminder sent
                    send_sms(
                        participant=part,
                        content="Please tell me a wishlist of three things YOU would love to receive this Christmas and I'll pass it along to your Secret Santa 🎅",
                    )
                    current_wishlist.reminder_sent = timezone.datetime.now()
                    current_wishlist.save()

                elif current_wishlist.reminder_sent < timezone.datetime.now() - timedelta(days=3):
                    # Been over a day since last reminder
                    send_sms(
                        participant=part,
                        content="Hello! It's Snowflake - remember to send me your wishlist, so that your Secret Santa can get wrapping 🎁🎁",
                    )
                    current_wishlist.reminder_sent = timezone.datetime.now()
                    current_wishlist.save()

                else:
                    # Been less than a day since we last asked. Get off their back.
                    pass
            
            elif r_wishlist.is_complete and not draw.recipient_wishlist_sent:
                send_sms(
                    participant=draw.participant,
                    content="Here is {}'s wishlist:\r \r{}\r \rHappy shopping and Merry Christmas 🎅✨🎄".format(
                        draw.recipient.name,
                        r_wishlist.content,
                    ),
                )
                draw.recipient_wishlist_sent = True

            draw.save()

        else:

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
            selected_user = eligble_users.order_by("?").first()
            DrawnName.objects.create(
                year=current_year,
                participant=part,
                recipient=selected_user,
            )

    return HttpResponse("Hello, world.")
