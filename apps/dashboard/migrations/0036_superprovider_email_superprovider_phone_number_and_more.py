# Generated by Django 4.2.9 on 2024-03-25 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0035_advence'),
    ]

    operations = [
        migrations.AddField(
            model_name='superprovider',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='superprovider',
            name='phone_Number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='advence',
            name='inquiry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.inquiry'),
        ),
    ]
