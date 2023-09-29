from typing import Optional
import logging

from django.db.models import Exists, OuterRef, Count, QuerySet

import blog.models as models


log = logging.getLogger(__name__)


def set_post_like(*, post_pk: int, user_pk: int, like: bool) -> int:
    """Like or unlike a blog post."""
    if like:
        models.Like.objects.update_or_create(post_id=post_pk, user_id=user_pk)
    else:
        models.Like.objects.filter(post_id=post_pk, user_id=user_pk).delete()

    return models.Like.objects.filter(post_id=post_pk).count()


def get_posts(user_pk: Optional[int] = None) -> 'QuerySet[models.Post]':
    """Return a blog.Posts queryset, annotated with likes flags for given user ID."""
    posts_q = models.Post.objects.prefetch_related('author', 'film', 'likes', 'comments')
    annotations = {'number_of_likes': Count('likes__id')}
    if user_pk:
        annotations.update(
            {'liked': Exists(models.Like.objects.filter(post_id=OuterRef('pk'), user_id=user_pk))}
        )
    return posts_q.annotate(**annotations).order_by(*models.Post._meta.ordering).distinct()
