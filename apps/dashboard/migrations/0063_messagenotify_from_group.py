# Generated by Django 4.2.9 on 2024-05-05 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0062_groupmessenger_messagegroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagenotify',
            name='from_group',
            field=models.BooleanField(default=False),
        ),
    ]