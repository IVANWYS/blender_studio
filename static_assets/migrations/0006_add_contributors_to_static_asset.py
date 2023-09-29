# Generated by Django 3.0.9 on 2021-08-17 10:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('static_assets', '0005_add_video_loop'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticasset',
            name='contributors',
            field=models.ManyToManyField(blank=True, help_text='People who contributed to creation of this asset.', to=settings.AUTH_USER_MODEL, verbose_name='contributors (optional)'),
        ),
    ]
