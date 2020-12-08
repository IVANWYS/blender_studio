# Generated by Django 3.0.9 on 2020-12-07 14:42

import common.upload_paths
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_add_can_view_content_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=common.upload_paths.get_upload_to_hashed_path),
        ),
    ]
