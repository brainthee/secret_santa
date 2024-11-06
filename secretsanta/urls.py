from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path("sms", views.sms_response, name="sms"),
    path("draw", views.draw_year, name="draw"),
    path("clear", views.clear, name="clear"),
]
