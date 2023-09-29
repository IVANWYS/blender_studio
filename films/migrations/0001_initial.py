# Generated by Django 3.0.9 on 2020-12-18 10:35

import common.mixins
import common.upload_paths
import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_published', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=512)),
                ('slug', models.SlugField(blank=True)),
                ('description', models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n')),
                ('category', models.CharField(choices=[('artwork', 'Artwork'), ('production_file', 'Production File'), ('production_lesson', 'Production Lesson')], db_index=True, max_length=17)),
                ('view_count', models.PositiveIntegerField(default=0, editable=False)),
                ('is_published', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_free', models.BooleanField(default=False)),
                ('is_spoiler', models.BooleanField(default=False)),
                ('contains_blend_file', models.BooleanField(default=False, help_text='Is the asset a .blend file or a package containing .blend files?')),
            ],
            options={
                'ordering': ['order', 'date_published'],
            },
        ),
        migrations.CreateModel(
            name='AssetComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=512)),
                ('slug', models.SlugField(default=common.upload_paths.shortuid, unique=True)),
                ('text', models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n')),
                ('thumbnail', models.FileField(blank=True, null=True, upload_to=common.upload_paths.get_upload_to_hashed_path)),
                ('thumbnail_aspect_ratio', models.CharField(choices=[('original', 'Original'), ('1:1', 'Square (1:1)'), ('16:9', 'Widescreen (16:9)'), ('4:3', 'Four-By-Three (4:3)')], default='original', help_text='Controls aspect ratio of the thumbnails shown in the gallery.', max_length=10)),
            ],
            options={
                'ordering': ['order', 'date_created'],
            },
            bases=(common.mixins.StaticThumbnailURLMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=512, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('summary', models.TextField()),
                ('status', models.TextField(choices=[('0_dev', 'In Development'), ('1_prod', 'In Production'), ('2_released', 'Released')])),
                ('release_date', models.DateField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('logo', models.FileField(upload_to=common.upload_paths.get_upload_to_hashed_path)),
                ('poster', models.FileField(upload_to=common.upload_paths.get_upload_to_hashed_path)),
                ('picture_header', models.FileField(upload_to=common.upload_paths.get_upload_to_hashed_path)),
                ('thumbnail', models.FileField(upload_to=common.upload_paths.get_upload_to_hashed_path)),
                ('youtube_link', models.URLField(blank=True)),
                ('show_production_logs_nav_link', models.BooleanField(default=False, help_text='Display a link to production logs in the navigation.')),
                ('show_production_logs_as_featured', models.BooleanField(default=False, help_text='Display production logs instead of the featured gallery on the film page.')),
                ('show_blog_posts', models.BooleanField(default=False, help_text='Display latest blog posts on the film page.')),
            ],
            options={
                'ordering': ('-release_date',),
            },
            bases=(common.mixins.StaticThumbnailURLMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FilmCrew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='FilmFlatPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='It will be displayed as the section name in the navigation bar.', max_length=50, verbose_name='Page title')),
                ('slug', models.SlugField(blank=True, help_text='The page slug has to be unique per film. If it is not filled, it will be the slugified page title.', verbose_name='Page slug')),
                ('content', models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n')),
                ('html_content', models.TextField(blank=True, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, help_text='If not provided, will be set to <em>"This week on [film title]"</em>.', max_length=512, verbose_name='production log title')),
                ('summary', models.TextField(blank=True)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('youtube_link', models.URLField(blank=True)),
                ('thumbnail', models.FileField(blank=True, upload_to=common.upload_paths.get_upload_to_hashed_path)),
            ],
            options={
                'verbose_name': 'production log',
                'verbose_name_plural': 'production logs',
                'ordering': ('-start_date', '-name'),
            },
            bases=(common.mixins.StaticThumbnailURLMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProductionLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('legacy_id', models.SlugField(blank=True)),
            ],
            options={
                'verbose_name': 'production log entry',
                'verbose_name_plural': 'production log entries',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ProductionLogEntryAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'production log entry asset',
            },
        ),
    ]
