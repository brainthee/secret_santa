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
    content = models.TextField(blank=True, null=True)
    reminder_sent = models.DateTimeField(blank=True, null=True)
    is_complete = models.BooleanField(default=False)

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

    intro_sent = models.BooleanField(default=False)
    drawn_1_sent = models.BooleanField(default=False)
    drawn_2_sent = models.BooleanField(default=False)
    drawn_3_sent = models.BooleanField(default=False)
    recipient_wishlist_sent = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{}: {} -> {}".format(
            self.year,
            self.participant,
            self.recipient
        )

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

    def __str__(self) -> str:
        return "{}: {} -> {}: {}".format(
            str(self.processed_datetime),
            self.from_number,
            self.to_number,
            self.body,
        )

    class Meta:
        # unique_together = ('participant', 'year',)
        ordering = ["-processed_datetime",]