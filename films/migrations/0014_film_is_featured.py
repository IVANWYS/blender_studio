# Generated by Django 3.0.4 on 2020-06-17 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0013_collections_storage_backend'),
    ]

    operations = [
        migrations.AddField(
            model_name='film', name='is_featured', field=models.BooleanField(default=False),
        ),
    ]
