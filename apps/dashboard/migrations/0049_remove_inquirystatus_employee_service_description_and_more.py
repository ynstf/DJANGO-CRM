# Generated by Django 4.2.9 on 2024-04-06 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0048_inquirystatus_employee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inquirystatus',
            name='employee',
        ),
        migrations.AddField(
            model_name='service',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='date_inq',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]