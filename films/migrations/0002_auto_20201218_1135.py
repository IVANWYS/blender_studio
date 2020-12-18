# Generated by Django 3.0.9 on 2020-12-18 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('static_assets', '0001_initial'),
        ('films', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewAsset',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('static_assets.staticasset',),
        ),
        migrations.AddField(
            model_name='productionlogentryasset',
            name='asset',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='entry_asset', to='films.Asset'),
        ),
        migrations.AddField(
            model_name='productionlogentryasset',
            name='production_log_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entry_assets', to='films.ProductionLogEntry'),
        ),
        migrations.AddField(
            model_name='productionlogentry',
            name='assets',
            field=models.ManyToManyField(through='films.ProductionLogEntryAsset', to='films.Asset'),
        ),
    ]
