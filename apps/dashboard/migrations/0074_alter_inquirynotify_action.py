# Generated by Django 4.2.9 on 2024-06-20 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0073_request_aproved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inquirynotify',
            name='action',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('connecting', 'connecting'), ('cancel', 'cancel'), ('send quotation', 'send quotation'), ('pending', 'pending'), ('underpreccess', 'underpreccess'), ('updated', 'updated'), ('reminder', 'reminder'), ('complain', 'complain'), ('done', 'done'), ('need approve', 'need approve'), ('approvement', 'approvement')], max_length=50, null=True),
        ),
    ]
