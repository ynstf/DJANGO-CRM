# Generated by Django 4.2.9 on 2024-03-23 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_uploadedimage_inquiry_cloudinary_urls_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UploadedImage',
        ),
    ]