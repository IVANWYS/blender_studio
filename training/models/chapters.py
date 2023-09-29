import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls.base import reverse

from common import mixins
from common.upload_paths import get_upload_to_hashed_path
from common.google_trans import trans_SC, trans_TC
from training.models import trainings
import common.help_texts


User = get_user_model()


class Chapter(mixins.CreatedUpdatedMixin, models.Model):
    class Meta:
        ordering = ['index', 'name']

    training = models.ForeignKey(
        trainings.Training, on_delete=models.CASCADE, related_name='chapters'
    )
    index = models.IntegerField()

    name = models.CharField(max_length=512)
    slug = models.SlugField(unique=True, null=False)
    description = models.TextField(blank=True, help_text=common.help_texts.markdown_with_html)
    picture_header = models.FileField(upload_to=get_upload_to_hashed_path, null=True, blank=True)
    thumbnail = models.FileField(upload_to=get_upload_to_hashed_path, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_published = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Trans name
        if self.name_zh_hans == None or self.name_zh_hans == "":
            self.name_zh_hans = trans_SC(self.name_en)
        if self.name_zh_hant == None or self.name_zh_hant == "":
            self.name_zh_hant = trans_TC(self.name_en)
        # Trans description
        if self.description_en != "":
            if self.description_zh_hans == "":
                self.description_zh_hans = trans_SC(self.description_en)
            if self.description_zh_hant == "":
                self.description_zh_hant = trans_TC(self.description_en)
        super(Chapter, self).save(*args, **kwargs)


    def clean(self) -> None:
        super().clean()
        if not self.slug:
            self.slug = uuid.uuid4().hex

    def __str__(self) -> str:
        return f'{self.training.name} > {self.index:02.0f}. {self.name}'

    def get_absolute_url(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        return reverse(
            'chapter', kwargs={'training_slug': self.training.slug, 'chapter_slug': self.slug},
        )

    @property
    def admin_url(self) -> str:
        return reverse('admin:training_chapter_change', args=[self.pk])
