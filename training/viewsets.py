"""API viewsets for trainings."""
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import mixins

import common.mixins
import training.models.sections
import training.serializers


class SectionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    common.mixins.SetModifiedByViewMixin,
    viewsets.GenericViewSet,
):
    """List, update or search training sections."""

    queryset = training.models.sections.Section.objects.all()
    serializer_class = training.serializers.SectionSerializer
    search_fields = [
        'chapter__name',
        'chapter__training__name',
        'name',
        'slug',
        'static_asset__author__email',
        'static_asset__author__full_name',
        'static_asset__original_filename',
        'static_asset__source',
        'static_asset__user__email',
        'static_asset__user__full_name',
        'user__email',
        'user__full_name',
    ]
    filter_backends = (filters.SearchFilter,)
