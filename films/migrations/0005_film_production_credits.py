# Generated by Django 3.0.14 on 2021-10-03 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('films', '0004_film_show_landing_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilmProductionCredit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('display_name', models.CharField(blank=True, max_length=128, null=True)),
                ('is_public', models.BooleanField(default=None, help_text='Display your name in the film credits.', null=True)),
                ('is_editable', models.BooleanField(default=True)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.Film')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_credits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'film')},
            },
        ),
    ]
