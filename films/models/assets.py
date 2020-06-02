from django.db import models
from django.utils.text import slugify

from common import mixins
from films.models import Collection


class AssetCategory(models.TextChoices):
    artwork = 'artwork', 'Artwork'
    production_file = 'production_file', 'Production File'
    production_lesson = 'production_lesson', 'Production Lesson'


class Asset(mixins.CreatedUpdatedMixin, models.Model):
    """ This represents the leaf of the tree of film-related resources.

    An asset can be of one of the three types: image, video, or file.
    """

    class Meta:
        constraints = []  # TODO: only one related file (img, video, file)

    static_asset = models.ForeignKey(
        'assets.StaticAsset', on_delete=models.CASCADE, related_name='assets'
    )

    collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.SET_NULL, related_name='assets'
    )
    order = models.IntegerField()
    name = models.CharField(max_length=512)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    category = models.CharField(choices=AssetCategory.choices, max_length=17, db_index=True)
    view_count = models.PositiveIntegerField(default=0)

    visibility = models.BooleanField(default=False)

    def clean(self) -> None:
        super().clean()
        if not self.slug:
            self.slug = slugify(self.name)

    def __str__(self) -> str:
        return self.name
