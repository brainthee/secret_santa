from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pprint import pprint
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from .models import *
from .utils import send_sms


@csrf_exempt
def sms_response(request):
    current_year = datetime.now().year
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
            content="Hmm, sorry {}! As a small but special elf, I'm not sure I understood your message. I've got your wishlist and you should know who your person is.".format(
                part.name,
            ),
        )
    else:
        if msg.body.lower() == "yes":
            send_sms(
                participant=part,
                content="Amazing! I've got: \"{}\". I'll let your secret santa know :)".format(
                    current_wishlist.content,
                    part.name,
                ),
            )
            current_wishlist.is_complete = True
            current_wishlist.save()
            draw = DrawnName.objects.get(year=current_year, recipient=part)
            draw.recipient_wishlist_sent = False
            draw.save()
        else:
            if current_wishlist.content:
                current_wishlist.content = str(current_wishlist.content) + "\n" + msg.body
            else:
                current_wishlist.content = msg.body
            current_wishlist.save()
            send_sms(
                participant=part,
                content="Got it. Is that everything? (Please say yes or just add more!)".format(
                    part.name,
                ),
            )

    return HttpResponse("OK")


@staff_member_required
def clear(request):
    DrawnName.objects.all().delete()
    WishList.objects.all().delete()


@staff_member_required
def draw_year(request):
    # DrawnName.objects.all().delete()
    # WishList.objects.all().delete()
    current_year = datetime.now().year
    for part in Participant.objects.all():
        current_wishlist,_ = WishList.objects.get_or_create(
            participant=part, year=current_year
        )

        if DrawnName.objects.filter(year=current_year, participant=part).exists():
            # Already drawn - see if we need to do any bits
            draw = DrawnName.objects.get(year=current_year, participant=part)
            if not draw.intro_sent:
                # Send intro text!
                print("Sending intro text to {}".format(part))
                send_sms(
                    participant=part,
                    content="Hey {name}! I'm Snowflake, the Secret Santa Helper. You've been invited to join in our Secret Santa group. Get ready for more info!".format(
                        name=part.name
                    ),
                )
                if not current_wishlist.is_complete:
                    send_sms(
                        participant=part,
                        content="It's almost time to meet your Secret Santa recipient! But first, we need your wish list! Please share 3 things you'd love to receive (no prices or hints, just fun surprises!). Please keep it to a single message.",
                    )
                draw.intro_sent = True

            elif not draw.drawn_sent:
                if current_wishlist.is_complete:
                    # Send draw info
                    print("Sending drawn text to {}".format(part))
                    send_sms(
                        participant=part,
                        content="Meet your Secret Santa recipient... It's {}! I'll send you their wishlist in a moment. Keep it a secret and get ready to surprise them on {}. Remember, the budget is no more than £{}".format(
                            draw.recipient.name,
                            settings.DRAW_DATE,
                            settings.DRAW_BUDGET,
                        ),
                    )
                    draw.drawn_sent = True
                else:
                    # Remind person to complete their wishlist
                    print("Sending wishlist reminder text to {}".format(part))
                    send_sms(
                        participant=part,
                        content="Hey {}, don't forget to share your Secret Santa wish list! We need 3 things you'd love to receive. Your recipient is counting on it... and so are our North Pole elves".format(
                            draw.participant.name,
                        ),
                    )

            elif not draw.recipient_wishlist_sent:
                # Send recip's wishlist...
                r_wishlist = WishList.objects.get(year=current_year, participant=draw.recipient)
                if r_wishlist.is_complete:
                    print("Sending recip's wishlist text to {}".format(part))
                    send_sms(
                        participant=part,
                        content="Here's {}'s wishlist! \"{}\"".format(
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
