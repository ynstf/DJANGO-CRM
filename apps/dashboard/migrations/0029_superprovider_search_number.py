# Generated by Django 4.2.9 on 2024-03-19 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0028_remove_superprovider_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='superprovider',
            name='search_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
