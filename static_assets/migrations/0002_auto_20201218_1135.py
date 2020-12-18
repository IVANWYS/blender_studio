# Generated by Django 3.0.9 on 2020-12-18 10:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('static_assets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideoprogress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_progress', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='uservideoprogress',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='static_assets.Video'),
        ),
        migrations.AddField(
            model_name='staticasset',
            name='author',
            field=models.ForeignKey(blank=True, help_text='The actual author of the artwork/learning materials', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='authored_assets', to=settings.AUTH_USER_MODEL, verbose_name='author (optional)'),
        ),
        migrations.AddField(
            model_name='staticasset',
            name='license',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='static_assets', to='static_assets.License'),
        ),
        migrations.AddField(
            model_name='staticasset',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='uploaded_assets', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='image',
            name='static_asset',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='static_assets.StaticAsset'),
        ),
        migrations.AddConstraint(
            model_name='uservideoprogress',
            constraint=models.UniqueConstraint(fields=('user', 'video'), name='unique_progress_per_user_and_video'),
        ),
    ]
