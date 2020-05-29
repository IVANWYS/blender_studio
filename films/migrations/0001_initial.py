# Generated by Django 3.0.4 on 2020-05-29 09:21

from django.db import migrations, models
import django.db.models.deletion
import films.models.collections
import films.models.films


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('title', models.TextField(unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('summary', models.TextField()),
                ('status', models.TextField(choices=[('pre_production', 'In Development'), ('in_production', 'In Production'), ('released', 'Released')])),
                ('visibility', models.BooleanField(default=False)),
                ('logo', models.FileField(upload_to=films.models.films.film_overview_upload_path)),
                ('poster', models.FileField(upload_to=films.models.films.film_overview_upload_path)),
                ('picture_header', models.FileField(blank=True, null=True, upload_to=films.models.films.film_overview_upload_path)),
                ('picture_16_9', models.FileField(blank=True, null=True, upload_to=films.models.films.film_overview_upload_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField()),
                ('name', models.CharField(max_length=512)),
                ('slug', models.SlugField(blank=True)),
                ('text', models.TextField()),
                ('picture_16_9', models.FileField(blank=True, null=True, upload_to=films.models.collections.collection_overview_upload_path)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='films.Film')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_collections', to='films.Collection')),
            ],
        ),
        migrations.AddConstraint(
            model_name='collection',
            constraint=models.UniqueConstraint(fields=('parent', 'order'), name='unique_ordering_per_collection'),
        ),
        migrations.AddConstraint(
            model_name='collection',
            constraint=models.UniqueConstraint(fields=('parent', 'slug'), name='unique_slug_per_collection'),
        ),
    ]
