# Generated by Django 4.2.9 on 2024-02-27 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_permission_employee_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='name',
            field=models.CharField(max_length=36, unique=True),
        ),
    ]
