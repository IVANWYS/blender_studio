# Generated by Django 3.0 on 2020-02-26 10:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
            ],
            options={'permissions': [('moderate_comment', 'Can moderate comments')],},
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                (
                    'comment',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='comments.Comment'
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='likes',
            field=models.ManyToManyField(
                related_name='liked_comments', through='comments.Like', to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='comment',
            name='reply_to',
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='replies',
                to='comments.Comment',
            ),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='comments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(
                fields=('user', 'comment'), name='only_one_like_per_comment_and_user'
            ),
        ),
    ]
