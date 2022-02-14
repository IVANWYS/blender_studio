from pathlib import PurePosixPath
from typing import Optional
import datetime
import logging
import mimetypes

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.urls.base import reverse
from django.utils.text import slugify

import looper.model_mixins

from common import mixins
from common.upload_paths import get_upload_to_hashed_path
from static_assets.models import License
from static_assets.tasks import create_video_processing_job, create_video_transcribing_job
import common.storage

User = get_user_model()
log = logging.getLogger(__name__)


def _get_default_license_id() -> Optional[int]:
    cc_by = License.objects.filter(slug='cc-by').first()
    return cc_by.pk if cc_by else None


class StaticAssetFileTypeChoices(models.TextChoices):
    file = 'file', 'File'
    image = 'image', 'Image'
    video = 'video', 'Video'


class StaticAsset(
    mixins.CreatedUpdatedMixin,
    mixins.StaticThumbnailURLMixin,
    looper.model_mixins.RecordModificationMixin,
    mixins.SaveAndRecordChangesMixin,
    models.Model,
):
    class Meta:
        ordering = ['-date_created']

    source = models.FileField(
        upload_to=get_upload_to_hashed_path,
        storage=common.storage.S3Boto3CustomStorage(),
        blank=True,
        max_length=256,
    )
    source_type = models.CharField(
        choices=StaticAssetFileTypeChoices.choices,
        max_length=5,
        default=StaticAssetFileTypeChoices.file,
    )
    # TODO(Natalia): source type validation
    original_filename = models.CharField(max_length=128, editable=False)
    size_bytes = models.BigIntegerField(editable=False)

    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='uploaded_assets', verbose_name='created by'
    )
    user.description = 'The user who created the static asset.'
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='authored_assets',
        verbose_name='author (optional)',
        help_text='The actual author of the artwork/learning materials',
    )
    author.description = 'The actual author of the artwork/learning materials.'
    license = models.ForeignKey(
        License,
        blank=True,
        null=True,
        default=_get_default_license_id,
        on_delete=models.SET_NULL,
        related_name='static_assets',
    )
    contributors = models.ManyToManyField(
        User,
        blank=True,
        help_text='People who contributed to creation of this asset.',
        verbose_name='contributors (optional)',
    )

    thumbnail = models.FileField(upload_to=get_upload_to_hashed_path, blank=True, max_length=256)
    thumbnail.description = (
        "Asset thumbnail is auto-generated for images and videos. Required for other files."
    )

    # Reference to legacy Blender Cloud file
    slug = models.SlugField(blank=True)

    content_type = models.CharField(max_length=256, blank=True)

    view_count = models.PositiveIntegerField(default=0, editable=False)
    download_count = models.PositiveIntegerField(default=0, editable=False)

    record_modification_fields = {
        'source',
        'source_type',
        'original_filename',
        'thumbnail',
        'content_type',
    }

    @property
    def author_name(self) -> str:
        """Get the asset's author full name.

        Usually the author of the asset will be the same as the user who uploads the asset.
        """
        author = self.author or self.user
        return author.full_name

    @property
    def author_image_url(self) -> str:
        """Get the asset's author's image.

        Usually the author of the asset will be the same as the user who uploads the asset.
        """
        author = self.author or self.user
        return author.image_url

    def process_video(self):
        """Create video processing task if asset has correct type."""
        if self.source_type != StaticAssetFileTypeChoices.video:
            return
        if not self.source:
            return
        # Create a background job, using only hashable arguments
        create_video_processing_job(self.id)

    def transcribe_video(self):
        """Create video transcribing task if asset has correct type."""
        if self.source_type != StaticAssetFileTypeChoices.video:
            return
        if not self.source:
            return
        # Create a background job, using only hashable arguments
        create_video_transcribing_job(self.id)

    def clean(self):
        super().clean()
        if not self.pk and self.source:
            # Save the original filename only on asset creation.
            self.original_filename = self.source.file.name

        if self.source:
            # The `if` prevents an unhandled exception if one tries to save without a source
            self.size_bytes = self.source.size
            content_type, _ = mimetypes.guess_type(self.original_filename)
            if not self.content_type:
                self.content_type = content_type
            if not content_type:
                self.source_type = StaticAssetFileTypeChoices.file
            elif 'image' in content_type:
                self.source_type = StaticAssetFileTypeChoices.image
            elif 'video' in content_type:
                self.source_type = StaticAssetFileTypeChoices.video

        if self.source_type == StaticAssetFileTypeChoices.file and not self.thumbnail:
            raise ValidationError(
                f'A thumnbnail has to be provided for `{self.source_type}` source type.'
            )

    def save(self, *args, **kwargs):
        created = self.pk is None
        self.full_clean()
        self.save_and_record_changes(*args, **kwargs)
        if not created:
            return
        # Create related tables for video or image
        if self.source_type == 'video':
            Video.objects.create(static_asset=self, duration=datetime.timedelta(seconds=0))
            self.process_video()
        elif self.source_type == 'image':
            # Use source image as a thumbnail
            if not self.thumbnail:
                self.thumbnail.name = self.source.name
                self.save(update_fields=['thumbnail'])
            Image.objects.create(static_asset=self)
            # TODO(fsiddi) Background job to update the image info

    def __str__(self):
        return f'({self.id}) {self.original_filename}'

    @property
    def content_disposition(self) -> Optional[str]:
        """Try to get a human-readable file name for Content-Disposition header."""
        path = PurePosixPath(self.source.name)
        ext = path.suffix
        filename = None

        if self.original_filename:
            filename = f'{slugify(PurePosixPath(self.original_filename).stem)}{ext}'

        if filename:
            return f'attachment; filename="{filename}"'

    @property
    def download_size(self) -> str:
        size_bytes = self.size_bytes
        if self.source_type == 'video':
            variation = self.video.default_variation
            if variation:
                size_bytes = variation.size_bytes
        if size_bytes:
            return filesizeformat(size_bytes)
        return ''

    @property
    def download_source(self):
        if self.source_type == 'video':
            return self.video.source if self.video else None
        return self.source

    @property
    def download_url(self) -> str:
        download_source = self.download_source
        if not download_source or not download_source.name:
            return ''
        return reverse('download-source-url', kwargs={'source': download_source.name})


class Video(models.Model):
    static_asset = models.OneToOneField(StaticAsset, on_delete=models.CASCADE)
    height = models.PositiveIntegerField(blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    resolution_label = models.CharField(max_length=32, blank=True)
    duration = models.DurationField(help_text='[DD] [[HH:]MM:]ss[.uuuuuu]')
    duration.description = 'Video duration in the format [DD] [[HH:]MM:]ss[.uuuuuu]'
    play_count = models.PositiveIntegerField(default=0, editable=False)
    loop = models.BooleanField(default=False)

    @property
    def duration_label(self):
        """A duration label that adaptively displays time.

        For example: 0:02, 1:02, 10:02, 1:20:01.
        """
        total_seconds = int(self.duration.total_seconds())
        remaining_hours = total_seconds % 86400
        remaining_minutes = remaining_hours % 3600
        hours = remaining_hours // 3600
        minutes = remaining_minutes // 60
        seconds = remaining_minutes % 60

        # Show hours only if present
        hours_str = f'{hours}:' if hours else ''

        # Show minutes with zero padding only if hours are present
        if minutes and hours:
            minutes_str = f'{minutes:02d}:'
        elif minutes:
            minutes_str = f'{minutes}:'
        # Show zero minutes when no minutes are present (0:12)
        else:
            minutes_str = '0:'
        # Always pad seconds display
        seconds_str = f'{seconds:02d}'
        return f'{hours_str}{minutes_str}{seconds_str}'

    @property
    def default_variation(self) -> Optional['VideoVariation']:
        return self.variations.first()

    @property
    def source(self):
        default_variation = self.default_variation
        # TODO(fsiddi) ensure that default_variation.source is never None
        if not default_variation or not default_variation.source:
            log.warning('Variation for video %i not found' % self.pk)
            return self.static_asset.source
        return default_variation.source

    @property
    def progress_url(self) -> str:
        return reverse('video-progress', kwargs={'video_pk': self.pk})

    def __str__(self) -> str:
        return f'{self._meta.model_name} {self.static_asset.original_filename}'

    @property
    def content_disposition(self) -> Optional[str]:
        """Try to get a human-readable file name for Content-Disposition header."""
        path = PurePosixPath(self.source.name)
        ext = path.suffix
        filename = None
        resolution_label = f'-{self.resolution_label}' if self.resolution_label else ''
        original_filename = self.static_asset.original_filename

        if original_filename:
            filename = f'{slugify(PurePosixPath(original_filename).stem)}{resolution_label}{ext}'

        if filename:
            return f'attachment; filename="{filename}"'

    def get_progress_position(self, user_id) -> Optional[datetime.timedelta]:
        """Get progress for a user with given ID."""
        try:
            progress = self.progress.get(user_id=user_id)
            return progress.position
        except ObjectDoesNotExist:
            pass
        return None


class VideoVariation(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='variations')
    height = models.PositiveIntegerField(blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    resolution_label = models.CharField(max_length=32, blank=True)
    source = models.FileField(upload_to=get_upload_to_hashed_path, blank=True, max_length=256)
    size_bytes = models.BigIntegerField(editable=False)
    content_type = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return f"Video variation for {self.video.static_asset.original_filename}"

    @property
    def content_disposition(self) -> Optional[str]:
        """Try to get a human-readable file name for Content-Disposition header."""
        path = PurePosixPath(self.source.name)
        ext = path.suffix
        filename = None
        resolution_label = f'-{self.resolution_label}' if self.resolution_label else ''
        original_filename = self.video.static_asset.original_filename

        section = getattr(self.video.static_asset, 'section', None)
        # This is a training section video, use its name as a file name
        if section:
            filename = f'{slugify(section.name)}{resolution_label}{ext}'
        elif original_filename:
            filename = f'{slugify(PurePosixPath(original_filename).stem)}{resolution_label}{ext}'

        if filename:
            return f'attachment; filename="{filename}"'


class VideoTrackLanguageCodeChoices(models.TextChoices):
    en_US = 'en-US', 'English'
    nl_NL = 'nl-NL', 'Nederlands'
    de_DE = 'de-DE', 'Deutsch'
    fr_FR = 'fr-FR', 'Français'
    ru_RU = 'ru-RU', 'Русский'


class VideoTrack(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='tracks')
    language = models.CharField(
        blank=False, null=False, max_length=5, choices=VideoTrackLanguageCodeChoices.choices
    )
    source = models.FileField(upload_to=get_upload_to_hashed_path, blank=True, max_length=256)

    @property
    def url(self) -> str:
        return reverse('video-track', kwargs={'pk': self.pk, 'path': self.source.name})


class Image(models.Model):
    static_asset = models.OneToOneField(StaticAsset, on_delete=models.CASCADE)
    height = models.PositiveIntegerField(blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    resolution_label = models.CharField(max_length=32, blank=True)

    def __str__(self) -> str:
        return f'{self._meta.model_name} {self.static_asset.original_filename}'


# TODO(Natalia): Handle deleting all these files when a model instance is deleted from the db?
