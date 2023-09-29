# Generated by Django 3.0.14 on 2021-10-14 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0008_videotrack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videotrack',
            name='language',
            field=models.CharField(choices=[('en-US', 'English'), ('nl-NL', 'Nederlands'), ('de-DE', 'Deutsch'), ('fr-FR', 'Français'), ('ru-RU', 'Русский')], max_length=5),
        ),
    ]
