from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from common import mixins
from common.upload_paths import get_upload_to_hashed_path
from common.google_trans import trans_SC, trans_TC
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class FilmStatus(models.TextChoices):
    in_development = '0_dev', _('In Development')
    in_production = '1_prod', _('In Production')
    released = '2_released', _('Released')


class Film(mixins.CreatedUpdatedMixin, mixins.StaticThumbnailURLMixin, models.Model):
    title = models.CharField(unique=True, max_length=512)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    description.description = 'Description consisting of a few sentences.'
    summary = models.TextField()
    summary.description = 'Summary consisting of multiple paragraphs.'

    status = models.TextField(choices=FilmStatus.choices)
    release_date = models.DateField(blank=True, null=True)
    release_date.description = "Past or planned release date of the film."
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    logo = models.FileField(
        upload_to=get_upload_to_hashed_path,
        help_text='A PNG picture with transparency, featuring the logo.',
    )
    poster = models.FileField(
        upload_to=get_upload_to_hashed_path, help_text='A 1508x2133 poster for the film.'
    )
    picture_header = models.FileField(
        upload_to=get_upload_to_hashed_path, help_text='A 1920x850 header image. No text.'
    )
    thumbnail = models.FileField(
        upload_to=get_upload_to_hashed_path, help_text='A 1920x1080 image for social media preview.'
    )
    youtube_link = models.URLField(blank=True)
    crew = models.ManyToManyField(User, through='FilmCrew')

    show_production_logs_nav_link = models.BooleanField(
        default=False,
        help_text='Display a link to production logs in the navigation.',
    )
    show_production_logs_as_featured = models.BooleanField(
        default=False,
        help_text='Display production logs instead of the featured gallery on the film page.',
    )
    show_blog_posts = models.BooleanField(
        default=False,
        help_text='Display latest blog posts on the film page.',
    )
    show_landing_page = models.BooleanField(
        default=False, help_text='Show a landing page to non-subscribers instead of film content'
    )

    class Meta:
        # Sort by release date descending,
        # fall back to created date in case the film hasn't been released yet.
        ordering = ('-release_date', '-date_created')

    def save(self, *args, **kwargs):
        # Trans title
        if self.title_zh_hans == None or self.title_zh_hans == "":
            self.title_zh_hans = trans_SC(self.title_en)
        if self.title_zh_hant == None or self.title_zh_hant == "":
            self.title_zh_hant = trans_TC(self.title_en)
        # Trans description
        if self.description_en != "":
            if self.description_zh_hans == "":
                self.description_zh_hans = trans_SC(self.description_en)
            if self.description_zh_hant == "":
                self.description_zh_hant = trans_TC(self.description_en)
        # Trans summary
        if self.summary_en != "":
            if self.summary_zh_hans == "":
                self.summary_zh_hans = trans_SC(self.summary_en)
            if self.summary_zh_hant == "":
                self.summary_zh_hant = trans_TC(self.summary_en)
        super(Film, self).save(*args, **kwargs)


    def clean(self) -> None:
        super().clean()
        if not self.slug:
            self.slug = slugify(self.title)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        return reverse('film-detail', kwargs={'film_slug': self.slug})

    @property
    def admin_url(self) -> str:
        return reverse('admin:films_film_change', args=[self.pk])


class FilmCrew(models.Model):
    """People that are involved in the film production.

    Used to set their role (Director, Animator, Art Director, etc) and
    display it in the production logs.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='film_crew')
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    role = models.CharField(max_length=128)

    class Meta:
        unique_together = ['user', 'film']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.role}"


class FilmProductionCredit(mixins.CreatedUpdatedMixin, models.Model):
    """Production Credit for subscribers.

    Credits are granted based on the amount of time a user kept their subscription
    active. Credits are opt-in. This means that by default a credit will not
    be displayed on the site and it will be ignored by the 'generate_production_credits_scroll'
    script.
    """

    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='production_credits')
    # Populated after running a one-time script, when locking the credit list
    display_name = models.CharField(max_length=128, blank=True, null=True)
    is_public = models.BooleanField(
        default=None,
        null=True,
        help_text='Display your name in the film credits.',
    )
    # Made not-editable after running a one-time script
    is_editable = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'film']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.film}"
