# Generated by Django 4.2.9 on 2024-08-07 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0087_alter_inquirynotify_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='vat',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]