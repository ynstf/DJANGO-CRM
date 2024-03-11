# Generated by Django 4.2.9 on 2024-03-11 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_alter_quotation_inquiry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inquiry',
            name='inq_num',
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.address'),
        ),
        migrations.AlterField(
            model_name='inquirynotify',
            name='action',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('connecting', 'connecting'), ('send quotation', 'send quotation'), ('pending', 'pending'), ('underpreccess', 'underpreccess'), ('updated', 'updated')], max_length=50, null=True),
        ),
    ]
