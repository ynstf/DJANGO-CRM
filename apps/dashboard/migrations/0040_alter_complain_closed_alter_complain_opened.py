# Generated by Django 4.2.9 on 2024-03-27 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0039_complain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complain',
            name='closed',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='complain',
            name='opened',
            field=models.DateField(blank=True, null=True),
        ),
    ]
