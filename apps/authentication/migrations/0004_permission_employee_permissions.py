# Generated by Django 4.2.9 on 2024-02-27 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_employee_sp_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='permissions',
            field=models.ManyToManyField(blank=True, null=True, to='authentication.permission'),
        ),
    ]