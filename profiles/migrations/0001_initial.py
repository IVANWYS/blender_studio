# Generated by Django 3.0.9 on 2020-12-18 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_read', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
    ]
