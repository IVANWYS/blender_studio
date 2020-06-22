# Generated by Django 3.0.4 on 2020-06-22 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0020_film_youtube_link_blank_not_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productionlogentryasset',
            name='production_log_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entry_assets', to='films.ProductionLogEntry'),
        ),
    ]
