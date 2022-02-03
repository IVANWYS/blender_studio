# noqa: D100
from typing import Dict, List, Literal, Union

from django.contrib.auth import get_user_model

from common import markdown
from common.types import assert_cast
from training.models import (
    chapters as chapters_models,
    sections as sections_models,
    trainings,
    flatpages,
    TrainingType,
)
from training.types import (
    ChapterNavigation,
    Navigation,
    SectionNavigation,
)

User = get_user_model()


def training_model_to_template(training: trainings.Training, favorited: bool) -> trainings.Training:
    training.favorited = favorited
    training.type = TrainingType(training.type)
    training.summary_rendered = markdown.render_unsafe(training.summary)
    training.tags_list = set(str(tag) for tag in training.tags.all())
    training.picture_header_url = '' if not training.picture_header else training.picture_header.url
    return training


def navigation_to_template(
    training: trainings.Training,
    chapters: List[chapters_models.Chapter],
    sections: List[sections_models.Section],
    *,
    user: User,
    current: Union[Literal['overview'], sections_models.Section, flatpages.TrainingFlatPage],
) -> Navigation:  # noqa: D103
    sections_per_chapter: Dict[int, List[sections_models.Section]] = {}
    for section in sections:
        sections_per_chapter.setdefault(section.chapter_id, []).append(section)

    return Navigation(
        overview_url=training.url,
        overview_active=current == 'overview',
        training_admin_url=(
            training.admin_url
            if user.is_staff and user.has_perm('training.change_training')
            else None
        ),
        chapters=[
            ChapterNavigation(
                index=chapter.index,
                name=chapter.name,
                slug=chapter.slug,
                url=chapter.url,
                current=(
                    isinstance(current, sections_models.Section)
                    and any(
                        current.id == section.id
                        for section in sections_per_chapter.get(chapter.id, [])
                    )
                    or isinstance(current, chapters_models.Chapter)
                    and current.id == chapter.id
                ),
                admin_url=(
                    chapter.admin_url
                    if user.is_staff and user.has_perm('training.change_chapter')
                    else None
                ),
                is_published=assert_cast(bool, getattr(chapter, 'is_published')),
                sections=[
                    SectionNavigation(
                        index=section.index,
                        name=section.name,
                        url=section.url,
                        started=assert_cast(bool, getattr(section, 'started')),
                        finished=assert_cast(bool, getattr(section, 'finished')),
                        progress_fraction=(
                            0
                            if getattr(section, 'video_position') is None
                            or getattr(section, 'video_duration') is None
                            else getattr(section, 'video_position')
                            / getattr(section, 'video_duration')
                        ),
                        current=(
                            isinstance(current, sections_models.Section)
                            and current.id == section.id
                        ),
                        is_free=assert_cast(bool, getattr(section, 'is_free')),
                        is_featured=assert_cast(bool, getattr(section, 'is_featured')),
                        is_published=assert_cast(bool, getattr(section, 'is_published')),
                        source_type=section.static_asset.source_type
                        if getattr(section, 'static_asset', None)
                        else None,
                        admin_url=(
                            section.admin_url
                            if user.is_staff and user.has_perm('training.change_section')
                            else None
                        ),
                    )
                    for section in sorted(
                        sections_per_chapter.get(chapter.id, []), key=lambda s: s.index
                    )
                ],
            )
            for chapter in sorted(chapters, key=lambda c: c.index)
        ],
    )


def recently_watched_sections_to_template(
    recently_watched_sections: List[sections_models.Section],
) -> List[sections_models.Section]:
    sections = []
    for section in recently_watched_sections:
        section.progress_fraction = (
            0
            if getattr(section, 'video_position') is None
            or getattr(section, 'video_duration') is None
            else getattr(section, 'video_position') / getattr(section, 'video_duration')
        )
        sections.append(section)
    return sections
