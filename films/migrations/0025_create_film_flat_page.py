# Generated by Django 3.0.8 on 2020-07-21 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0024_add_film_crew'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilmFlatPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(help_text='The page slug has to be unique per film. It also serves as the title of a subsection of a film\'s page, e.g. "about".', verbose_name='Page slug')),
                ('content', models.TextField(blank=True, help_text='Format the content in <a href="https://commonmark.org/help/">Markdown</a>.')),
                ('html_content', models.TextField(blank=True, editable=False)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flatpages', to='films.Film')),
            ],
        ),
        migrations.AddConstraint(
            model_name='filmflatpage',
            constraint=models.UniqueConstraint(fields=('slug', 'film'), name='unique_film_flat_page_url'),
        ),
    ]
