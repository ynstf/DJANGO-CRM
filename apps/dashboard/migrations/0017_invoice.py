# Generated by Django 4.2.9 on 2024-03-13 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_alter_permission_name'),
        ('dashboard', '0016_rename_total_booking_booking_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation_date', models.DateField(blank=True, null=True)),
                ('data', models.TextField(blank=True, null=True)),
                ('total', models.CharField(blank=True, max_length=50, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.customer')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.employee')),
                ('inquiry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.inquiry')),
                ('quotation_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.service')),
            ],
        ),
    ]
