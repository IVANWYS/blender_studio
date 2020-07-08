# Generated by Django 3.0.4 on 2020-06-14 16:17

from django.db import migrations, models
import django.db.models.deletion


def set_backend_asset(apps, schema_editor):
    Asset = apps.get_model('training', 'Asset')
    for asset in Asset.objects.all().iterator():
        asset.storage_backend = asset.section.chapter.training.storage_backend
        asset.save()


def set_backend_video(apps, schema_editor):
    Video = apps.get_model('training', 'Video')
    for video in Video.objects.all().iterator():
        video.storage_backend = video.section.chapter.training.storage_backend
        video.save()


def reverse_func(apps, schema_editor):
    pass  # Nothing do to


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0004_squashed_0010_alter_fields_in_models'),
        ('training', '0011_add_dynamic_file_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='storage_backend',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='static_assets.StorageBackend'),
            preserve_default=False,
        ),
        migrations.RunPython(set_backend_asset, reverse_func),
        migrations.AlterField(
            model_name='asset',
            name='storage_backend',
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.CASCADE, to='static_assets.StorageBackend'),
        ),
        migrations.AddField(
            model_name='video',
            name='storage_backend',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='static_assets.StorageBackend'),
            preserve_default=False,
        ),
        migrations.RunPython(set_backend_video, reverse_func),
        migrations.AlterField(
            model_name='video',
            name='storage_backend',
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.CASCADE, to='static_assets.StorageBackend'),
        ),
    ]
