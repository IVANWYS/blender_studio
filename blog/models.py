import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from comments.models import Comment
from common import mixins, markdown
from common.upload_paths import get_upload_to_hashed_path
from common.google_trans import trans_SC, trans_TC
from films.models import Film
import common.help_texts
import static_assets.models as models_static_assets

User = get_user_model()


class Post(mixins.CreatedUpdatedMixin, mixins.StaticThumbnailURLMixin, models.Model):
    class Meta:
        ordering = ('-date_published',)

    film = models.ForeignKey(
        Film, blank=True, null=True, on_delete=models.CASCADE, related_name='posts'
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='authored_posts')
    slug = models.SlugField(max_length=128)
    date_published = models.DateTimeField(blank=True, null=True)
    legacy_id = models.CharField(max_length=256, blank=True)
    is_published = models.BooleanField(default=False)

    title = models.CharField(max_length=512)
    category = models.CharField(max_length=128, blank=True)
    excerpt = models.TextField(
        blank=True, help_text='An optional short description displayed on the blog card.'
    )
    content = models.TextField(help_text=common.help_texts.markdown_with_html)
    content_html = models.TextField(blank=True, editable=False)
    thumbnail = models.FileField(
        upload_to=get_upload_to_hashed_path,
        blank=True,
        help_text='A 1920x1080 picture for the blog list and on social media.',
    )
    header = models.FileField(
        upload_to=get_upload_to_hashed_path,
        blank=True,
        help_text='A 2048x640 picture for the blog header. Can be abstract.',
    )

    comments = models.ManyToManyField(Comment, through='PostComment', related_name='post')
    attachments = models.ManyToManyField(models_static_assets.StaticAsset, blank=True)

    def __str__(self):
        return self.slug

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Generates the html version of the content and saves the object."""
        if not self.slug:
            self.slug = slugify(self.title)
        # Trans title
        if self.title_zh_hans == None or self.title_zh_hans == "":
            self.title_zh_hans = trans_SC(self.title_en)
        if self.title_zh_hant == None or self.title_zh_hant == "":
            self.title_zh_hant = trans_TC(self.title_en)
        # Trans excerpt
        if self.excerpt_en != "":
            if self.excerpt_zh_hans == "":
                self.excerpt_zh_hans = trans_SC(self.excerpt_en)
            if self.excerpt_zh_hant == "":
                self.excerpt_zh_hant = trans_TC(self.excerpt_en)
        # Trans content
        if self.content_en != "":
            if self.content_zh_hans == "":
                self.content_zh_hans = trans_SC(self.content_en)
            if self.content_zh_hant == "":
                self.content_zh_hant = trans_TC(self.content_en)
        # Clean but preserve some of the HTML tags
        self.content = markdown.clean(self.content)
        self.content_html = markdown.render_unsafe(self.content)
        self.content_en = markdown.clean(self.content_en)
        self.content_html_en = markdown.render_unsafe(self.content_en)
        self.content_zh_hans = markdown.clean(self.content_zh_hans)
        self.content_html_zh_hans = markdown.render_unsafe(self.content_zh_hans)
        self.content_zh_hant = markdown.clean(self.content_zh_hant)
        self.content_html_zh_hant = markdown.render_unsafe(self.content_zh_hant)
        # Set publish date if it's not set and the post is published
        if not self.date_published and self.is_published:
            self.date_published = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_new(self) -> bool:
        return self.date_published > timezone.now() - datetime.timedelta(days=7)

    def get_absolute_url(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        return reverse('post-detail', kwargs={'slug': self.slug})

    @property
    def comment_url(self) -> str:
        return reverse('api-post-comment', kwargs={'post_pk': self.pk})

    @property
    def like_url(self) -> str:
        return reverse('api-post-like', kwargs={'post_pk': self.pk})

    @property
    def admin_url(self) -> str:
        return reverse('admin:blog_post_change', args=[self.pk])


class PostComment(models.Model):
    """An intermediary model between Post and Comment.

    A PostComment should in fact only relate to one Comment, hence the
    OneToOne comment field.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE)

    def get_absolute_url(self) -> str:
        return self.post.url


class Like(mixins.CreatedUpdatedMixin, models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='only_one_like_per_post_and_user')
        ]

    # Whenever a User is deleted their Like lives on to ensure integrity of the conversation.
    # Instead, we remove the reference to the User to honor the deletion request as much as
    # possible.
    user = models.ForeignKey(
        User, null=True, blank=False, on_delete=models.SET_NULL, related_name='liked_posts'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    def __str__(self) -> str:
        return f'Like by {self.username} on {self.post}'

    @property
    def username(self) -> str:
        return '<deleted>' if self.user is None else self.user.username
