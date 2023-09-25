import logging

from actstream import action
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from comments.models import Comment, Like
from common import markdown
from users.queries import create_action_from_like

logger = logging.getLogger(__name__)


def _create_action_from_reply(user, comment: Comment) -> None:
    target = comment.reply_to
    verb = 'replied to'
    action.send(user, verb=verb, action_object=comment, target=target, public=False)


@receiver(pre_save, sender=Comment)
def clean_message(sender: object, instance: Comment, **kwargs: object) -> None:
    """Clean comment message and pre-render HTML for it."""
    instance.message = markdown.sanitize(instance.message)
    instance.message_html = markdown.render(instance.message)


@receiver(post_save, sender=Like)
def notify_about_like(sender: object, instance: Like, created: bool, **kwargs: object) -> None:
    """Generate notifications about comments likes."""
    if not created:
        return

    # Don't notify when one likes their own comments
    if instance.user == instance.comment.user:
        return

    target = instance.comment.get_action_target()
    create_action_from_like(actor=instance.user, target=target, action_object=instance.comment)


@receiver(post_save, sender=Comment)
def notify_about_reply(sender: object, instance: Comment, created: bool, **kwargs: object) -> None:
    """Generate notifications about comment replies."""
    if not created:
        return

    if not instance.reply_to:
        return

    # Don't notify when one replies to their own comments
    if instance.reply_to.user == instance.user:
        return

    _create_action_from_reply(instance.user, instance)


@receiver(post_delete, sender=Comment)
def delete_notifications(sender: object, instance: Comment, **kwargs: object) -> None:
    """Delete notifications linked to a comment that was deleted."""
    if not instance.pk:
        return

    comment_content_type = ContentType.objects.get_for_model(Comment)
    comment_id = instance.pk

    qs = Action.objects.filter(
        Q(action_object_content_type=comment_content_type, action_object_object_id=comment_id)
        | Q(target_content_type=comment_content_type, target_object_id=comment_id)
    )
    qs.delete()
