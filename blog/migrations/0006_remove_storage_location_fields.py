# Generated by Django 3.0.10 on 2020-09-30 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_update_file_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='revision',
            name='storage_location',
        ),
    ]
