# Generated by Django 4.2.9 on 2024-03-15 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_inquiryreminder'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='reminder_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inquirynotify',
            name='action',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('connecting', 'connecting'), ('send quotation', 'send quotation'), ('pending', 'pending'), ('underpreccess', 'underpreccess'), ('updated', 'updated'), ('reminder', 'reminder')], max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='SuperProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.service')),
            ],
        ),
    ]
