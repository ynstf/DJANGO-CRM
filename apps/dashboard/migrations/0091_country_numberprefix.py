# Generated by Django 4.2.9 on 2024-08-11 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0090_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='numberPrefix',
            field=models.CharField(default='', max_length=5),
            preserve_default=False,
        ),
    ]
