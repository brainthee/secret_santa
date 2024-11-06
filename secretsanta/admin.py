from django.contrib import admin
from .models import *


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["name", "number"]

@admin.register(Exclusions)
class ExclusionsAdmin(admin.ModelAdmin):
    pass

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ["participant", "year", "is_complete", "content"]

@admin.register(DrawnName)
class DrawnNameAdmin(admin.ModelAdmin):
    list_display = [
        "year", 
        "participant", 
        "intro_sent", 
        "drawn_1_sent", 
        "drawn_2_sent", 
        "drawn_3_sent", 
        "recipient_wishlist_sent"
        ]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["processed_datetime", "participant", "from_number", "to_number", "body"]
