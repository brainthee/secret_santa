# Generated by Django 5.1.2 on 2024-11-04 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretsanta', '0004_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='drawnname',
            name='drawn_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='drawnname',
            name='intro_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='drawnname',
            name='recipient_wishlist_sent',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
