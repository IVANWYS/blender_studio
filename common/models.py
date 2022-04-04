from django.db import models

from common import mixins
from common import validators


class TemplateVariable(mixins.CreatedUpdatedMixin, models.Model):
    """Store text and/or images to be used in templates.

    Currently, only front page '/' and '/welcome/' load these into their
    template contexts.
    N.B.: it's up to the templates to access and handles these correctly.
    """

    key = models.CharField(
        blank=False,
        help_text="Name of the variable, use this to access the variable in the template context.",
        max_length=30,
        null=False,
        unique=True,
        validators=[validators.validate_variable_key],
    )
    text = models.TextField(
        blank=True,
        default='',
        help_text=(
            'Text value of the variable.'
            ' Use "{{ key.text }}" to refer to this value in a template.'
        ),
        max_length=500,
        null=False,
    )
    image = models.ImageField(
        null=True,
        blank=True,
        help_text=(
            'Image value of the variable.'
            ' Use "{{ key.url }}" to access URL of this image in a template.'
        ),
    )

    class Meta:
        ordering = ['key']

    def __str__(self) -> str:
        return f'TemplateVariable "{self.key}"'

    def __bool__(self):
        return bool(self.image) or bool(self.text)

    def url(self) -> str:
        return self.image.url if self.image else ''
