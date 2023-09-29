# Generated by Django 3.0.14 on 2021-11-04 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_add_static_asset_view_download'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticAssetCountedVisit',
            fields=[
                ('field', models.CharField(choices=[('view_count', 'View Count'), ('download_count', 'Download Count')], max_length=20, primary_key=True, serialize=False)),
                ('last_seen_id', models.PositiveIntegerField()),
            ],
        ),
    ]
