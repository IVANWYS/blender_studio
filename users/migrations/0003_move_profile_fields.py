# Generated by Django 3.0.9 on 2020-12-21 10:55

import common.upload_paths
from django.core.paginator import Paginator
from django.db import migrations, models
BATCH_SIZE = 600


def copy_profile_values(apps, schema_editor):
    Profile = apps.get_model('profiles', 'Profile')
    User = apps.get_model('users', 'User')
    to_update = []
    p = Paginator(
        Profile.objects.select_related('user').order_by('user_id').all(),
        BATCH_SIZE,
        orphans=0,
        allow_empty_first_page=False,
    )
    if not p.num_pages:
        return

    for page_num in range(1, p.num_pages + 2):
        page = p.get_page(page_num)
        page.object_list
        for profile in page.object_list:
            user = profile.user
            user.is_subscribed_to_newsletter = profile.is_subscribed_to_newsletter
            user.image = profile.image
            user.full_name = profile.full_name
            to_update.append(user)
    User.objects.bulk_update(
        to_update,
        ['image', 'full_name', 'is_subscribed_to_newsletter'],
        batch_size=BATCH_SIZE,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20201218_1135'),
        ('users', '0002_unique_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('can_view_content', 'Can view subscription-only content')]},
        ),
        migrations.AddField(
            model_name='user',
            name='full_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=common.upload_paths.get_upload_to_hashed_path),
        ),
        migrations.AddField(
            model_name='user',
            name='is_subscribed_to_newsletter',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(copy_profile_values, reverse_code=migrations.RunPython.noop),
    ]
