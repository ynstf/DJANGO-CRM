# Generated by Django 4.2.9 on 2024-08-12 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0093_remove_service_vat_country_email_country_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]