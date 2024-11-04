from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Participant(models.Model):
    name = models.CharField(max_length=255)
    number = PhoneNumberField()

    class Meta:
        # unique_together = ('participant', 'year',)
        ordering = ["name",]

    def __str__(self) -> str:
        return "{} ({})".format(
            self.name,
            self.number
        )

class WishList(models.Model):
    participant = models.ForeignKey(Participant, related_name="wishlist", on_delete=models.CASCADE)
    year = models.IntegerField()

    class Meta:
        unique_together = ('participant', 'year',)

class Exclusions(models.Model):
    selected = models.ManyToManyField(Participant, related_name="excluded")

    def __str__(self) -> str:
        name = ""
        for sel in self.selected.all():
            if name:
                name = name + ", "                
            name = name + sel.name
        return name
        

class DrawnName(models.Model):
    year = models.IntegerField()
    participant = models.ForeignKey(Participant, related_name="draws", on_delete=models.CASCADE)
    recipient = models.ForeignKey(Participant, related_name="givers", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('year', 'participant',)
        

class Message(models.Model):
    processed_datetime = models.DateTimeField("Processed", auto_now=True)
    from_number = models.CharField("From", max_length=20)
    to_number = models.CharField("From", max_length=20)
    participant = models.ForeignKey(Participant, related_name="messages", on_delete=models.CASCADE)
    is_received = models.BooleanField("Is Received", default=True)
    body = models.TextField()
    smssid = models.CharField("MessageSID", max_length=200)

    class Meta:
        # unique_together = ('participant', 'year',)
        ordering = ["-processed_datetime",]