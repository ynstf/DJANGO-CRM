# Generated by Django 4.2.9 on 2024-07-16 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0084_points_inquiry'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquirynotify',
            name='point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.points'),
        ),
        migrations.AlterField(
            model_name='inquirynotify',
            name='action',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('connecting', 'connecting'), ('cancel', 'cancel'), ('send quotation', 'send quotation'), ('send bill', 'send bill'), ('pending', 'pending'), ('underpreccess', 'underpreccess'), ('updated', 'updated'), ('reminder', 'reminder'), ('complain', 'complain'), ('done', 'done'), ('need approve', 'need approve'), ('approvement', 'approvement'), ('new point', 'new point')], max_length=50, null=True),
        ),
    ]