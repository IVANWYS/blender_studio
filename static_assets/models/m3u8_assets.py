from django.db import models
from django.utils.translation import gettext_lazy as _
from static_assets.models import StaticAsset
from common.upload_paths import shortuid
import re


def SourcePATH(instance, filename):
    types = instance.types
    if types == AssetsTypes.PLAYLIST:
        title = instance.title
        slug = instance.slug
        return '/'.join(["M3U8", title, slug, filename])
    else:
        title = instance.title.title
        print(title)
        print(instance.title)
        slug = instance.title.slug
        return '/'.join(["M3U8", title, slug, types, filename])
    

class AssetsTypes(models.TextChoices):
    PLAYLIST = 'playlist', _('Playlist')
    VIDEO = 'video', _('Video')
    AUDIO = 'audio', _('Audio')


class M3u8Playlist(models.Model):
    title = models.CharField(max_length=255)
    types = models.CharField(choices=AssetsTypes.choices, max_length=200)
    source = models.FileField(upload_to=SourcePATH, null=True, blank=True, max_length=255)
    sVideo = models.ForeignKey(StaticAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name = "M3U8Video")
    slug = models.SlugField(default=shortuid)

    def save(self, *args, **kwargs):
        self.title = re.sub(r'[\W_]+', '-', self.title)

        super(M3u8Playlist, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class M3u8Source(models.Model):
    title = models.ForeignKey(M3u8Playlist, on_delete=models.CASCADE, related_name = "M3U8Source")
    types = models.CharField(choices=AssetsTypes.choices, max_length=200)
    source = models.FileField(upload_to=SourcePATH, null=True, blank=True, max_length=255)

    def __str__(self):
        return f"{self.title}"