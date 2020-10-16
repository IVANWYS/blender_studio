# Generated by Django 3.0.8 on 2020-07-09 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0014_storage_on_delete_protect'),
        ('training', '0016_rename_storage_backend_fields'),
    ]

    operations = [
        migrations.RemoveField(model_name='asset', name='size',),
        migrations.AddField(
            model_name='asset',
            name='size_bytes',
            field=models.IntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asset',
            name='storage_location',
            field=models.ForeignKey(
                null=True,
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                to='static_assets.StorageLocation',
            ),
        ),
        migrations.AlterField(
            model_name='video',
            name='storage_location',
            field=models.ForeignKey(
                null=True,
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                to='static_assets.StorageLocation',
            ),
        ),
    ]
