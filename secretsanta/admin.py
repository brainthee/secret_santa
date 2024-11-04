from django.contrib import admin
from .models import *


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass

@admin.register(Exclusions)
class ExclusionsAdmin(admin.ModelAdmin):
    pass

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    pass

@admin.register(DrawnName)
class DrawnNameAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
