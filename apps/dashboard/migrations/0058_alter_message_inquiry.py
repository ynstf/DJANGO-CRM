# Generated by Django 4.2.9 on 2024-04-29 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0057_address_location_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='inquiry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.inquiry'),
        ),
    ]
