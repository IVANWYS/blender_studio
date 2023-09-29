# Generated by Django 3.0.14 on 2021-10-29 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0010_set_source_type_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticasset',
            name='download_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='staticasset',
            name='view_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
