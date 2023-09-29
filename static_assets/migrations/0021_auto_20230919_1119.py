# Generated by Django 3.2.16 on 2023-09-19 03:19

import common.upload_paths
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0020_alter_staticasset_original_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='slug',
            field=models.SlugField(blank=True, default=common.upload_paths.shortuid),
        ),
        migrations.AddField(
            model_name='videotrack',
            name='slug',
            field=models.SlugField(blank=True, default=common.upload_paths.shortuid),
        ),
    ]
