# Generated by Django 4.2.9 on 2024-03-13 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_employeeaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='total',
            new_name='booking_number',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='data',
            new_name='details',
        ),
    ]