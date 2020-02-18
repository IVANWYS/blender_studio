from __future__ import annotations

from pathlib import Path

from django.db import models
from django.urls.base import reverse

from training_main.models import mixins, chapters


class Section(mixins.CreatedUpdatedMixin, models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['chapter', 'index'], name='unique_index_per_section'),
        ]

    chapter = models.ForeignKey(chapters.Chapter, on_delete=models.CASCADE, related_name='sections')
    index = models.IntegerField()

    name = models.TextField(unique=True)
    slug = models.SlugField(unique=True)
    text = models.TextField()

    def __str__(self) -> str:
        return f'{self.chapter.training.name} > {self.chapter.index}. {self.chapter.name} > {self.index}. {self.name}'

    @property
    def url(self) -> str:
        return reverse(
            'section',
            kwargs={
                'training_slug': self.chapter.training.slug,
                'chapter_index': self.chapter.index,
                'chapter_slug': self.chapter.slug,
                'section_index': self.index,
                'section_slug': self.slug,
            },
        )


def video_upload_path(video: Video, filename: str) -> str:
    return str(
        Path('trainings')
        / str(video.section.chapter.training.id)
        / 'chapters'
        / str(video.section.chapter.index)
        / 'sections'
        / str(video.section.index)
        / 'video'
        / filename
    )


class Video(mixins.CreatedUpdatedMixin, models.Model):
    section = models.OneToOneField(Section, on_delete=models.CASCADE, related_name='video')
    file = models.FileField(upload_to=video_upload_path)
    size = models.IntegerField()

    def __str__(self) -> str:
        return self.file.path  # type: ignore


def asset_upload_path(asset: Asset, filename: str) -> str:
    return str(
        Path('trainings')
        / str(asset.section.chapter.training.id)
        / 'chapters'
        / str(asset.section.chapter.index)
        / 'sections'
        / str(asset.section.index)
        / 'assets'
        / filename
    )


class Asset(mixins.CreatedUpdatedMixin, models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to=asset_upload_path)
    size = models.IntegerField()

    def __str__(self) -> str:
        return self.file.path  # type: ignore
