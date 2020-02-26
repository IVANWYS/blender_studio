# Generated by Django 3.0 on 2020-02-26 10:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(model_name='sectioncomment', name='unique_section_comment',),
        migrations.AddConstraint(
            model_name='sectioncomment',
            constraint=models.UniqueConstraint(
                fields=('comment',), name='unique_section_per_comment'
            ),
        ),
    ]
