# Generated by Django 4.2.9 on 2024-03-27 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0040_alter_complain_closed_alter_complain_opened'),
    ]

    operations = [
        migrations.AddField(
            model_name='complain',
            name='fixe_detail',
            field=models.TextField(blank=True, null=True),
        ),
    ]
