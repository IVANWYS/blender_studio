# Generated by Django 3.0.9 on 2020-08-19 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0018_training_and_section_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='type',
            field=models.TextField(choices=[('workshop', 'Workshop'), ('course', 'Course')]),
        ),
    ]
