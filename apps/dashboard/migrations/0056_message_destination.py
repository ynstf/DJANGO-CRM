# Generated by Django 4.2.9 on 2024-04-19 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_remove_employee_sp_service_employee_sp'),
        ('dashboard', '0055_alter_quotation_invoice_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recive_messages', to='authentication.employee'),
        ),
    ]
