# Generated by Django 4.2.9 on 2024-03-26 00:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0037_remove_superprovider_service_superprovider_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquirynotify',
            name='sp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.superprovider'),
        ),
    ]
