# Generated by Django 3.2.16 on 2023-08-29 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('static_assets', '0013_m3u8source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videotrack',
            name='language',
            field=models.CharField(choices=[('en-US', 'English'), ('zh-hans', '简体中文'), ('zh-hant', '繁體中文')], max_length=10),
        ),
    ]
