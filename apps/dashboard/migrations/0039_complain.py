# Generated by Django 4.2.9 on 2024-03-27 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0038_inquirynotify_sp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opened', models.DateTimeField(auto_now=True, null=True)),
                ('detail', models.TextField(blank=True, null=True)),
                ('closed', models.DateTimeField(auto_now=True, null=True)),
                ('inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.inquiry')),
            ],
        ),
    ]
