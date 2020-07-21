# Generated by Django 3.0.8 on 2020-07-08 09:42

import static_assets.models.static_assets
import common.upload_paths
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0011_squashed_0012_rename_storage_backend'),
        ('films', '0020_squashed_0025_alter_model_fields_and_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productionlog',
            name='picture_16_9',
            field=static_assets.models.static_assets.DynamicStorageFileField(
                upload_to=common.upload_paths.get_upload_to_hashed_path
            ),
        ),
        migrations.AlterField(
            model_name='productionlog',
            name='storage_location',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='production_logs',
                to='static_assets.StorageLocation',
            ),
        ),
    ]
