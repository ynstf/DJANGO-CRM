# Generated by Django 4.2.9 on 2024-06-20 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0072_request_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='aproved',
            field=models.BooleanField(default=False),
        ),
    ]
