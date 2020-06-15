from django.db import models
from django.urls.base import reverse
from django.utils.text import slugify

from assets.models import DynamicStorageFileField, StorageBackend
from common import mixins
from common.upload_paths import get_upload_to_hashed_path
from films.models import films


class Collection(mixins.CreatedUpdatedMixin, models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent', 'slug'], name='unique_slug_per_collection'),
        ]

    film = models.ForeignKey(films.Film, on_delete=models.CASCADE, related_name='collections')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='child_collections'
    )
    order = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=512)
    slug = models.SlugField(blank=True)
    text = models.TextField(blank=True)

    storage_backend = models.ForeignKey(StorageBackend, on_delete=models.CASCADE)
    preview = DynamicStorageFileField(upload_to=get_upload_to_hashed_path, blank=True, null=True)
    picture_16_9 = DynamicStorageFileField(upload_to=get_upload_to_hashed_path, blank=True, null=True)

    def clean(self) -> None:
        super().clean()
        if not self.slug:
            self.slug = slugify(self.name)

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        return reverse(
            'collection-detail', kwargs={'film_slug': self.film.slug, 'collection_slug': self.slug}
        )
