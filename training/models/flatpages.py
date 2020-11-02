"""Custom flat pages for training."""
from typing import Any

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from common import mixins, markdown
from training.models import Training
import static_assets.models as models_static_assets


class TrainingFlatPage(mixins.CreatedUpdatedMixin, models.Model):
    """Stores a single training-related flat page."""

    class Meta:  # noqa: D106
        constraints = [
            # The slug and training slug are used in the page url, which has to be unique.
            models.UniqueConstraint(
                fields=['slug', 'training'], name='unique_training_flat_page_url'
            ),
        ]

    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='flatpages')
    title = models.CharField(
        'Page title',
        max_length=50,
        help_text='It will be displayed as the section name in the navigation bar.',
    )
    slug = models.SlugField(
        'Page slug',
        blank=True,
        help_text=(
            'The page slug has to be unique per training. '
            'If it is not filled, it will be the slugified page title.'
        ),
    )
    content = models.TextField(
        blank=True,
        help_text='Format the content in <a href="https://commonmark.org/help/">Markdown</a>.',
    )
    html_content = models.TextField(blank=True, editable=False)
    attachments = models.ManyToManyField(models_static_assets.StaticAsset, blank=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Generate the html version of the content and saves the object."""
        if not self.slug:
            self.slug = slugify(self.title)
        self.html_content = markdown.render(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Flat page "{self.title}" of the training {self.training.name}'

    def get_absolute_url(self) -> str:  # noqa: D102
        return self.url

    @property
    def url(self) -> str:  # noqa: D102
        return reverse(
            'training-flatpage',
            kwargs={'training_slug': self.training.slug, 'page_slug': self.slug},
        )

    @property
    def admin_url(self) -> str:  # noqa: D102
        return reverse('admin:training_trainingflatpage_change', args=[self.pk])
