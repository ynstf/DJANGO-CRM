# Generated by Django 4.2.9 on 2024-03-28 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_remove_employee_sp_service_employee_sp'),
        ('dashboard', '0043_remove_message_destination'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recive_messages', to='authentication.employee'),
        ),
    ]