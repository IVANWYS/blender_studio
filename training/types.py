from __future__ import annotations

from typing import List, Optional, TypedDict
import dataclasses as dc


@dc.dataclass
class Navigation:
    training_admin_url: Optional[str]

    overview_url: str
    overview_active: bool

    chapters: List[ChapterNavigation]


@dc.dataclass
class ChapterNavigation:
    index: int
    name: str
    slug: str
    current: bool
    is_published: bool

    admin_url: Optional[str]
    url: Optional[str]

    sections: List[SectionNavigation]


@dc.dataclass
class SectionNavigation:
    index: int
    name: str
    url: str
    started: bool
    finished: bool
    progress_fraction: float
    current: bool
    is_free: bool
    is_featured: bool
    is_published: bool
    source_type: str

    admin_url: Optional[str]


class SectionProgressReportingData(TypedDict):
    progress_url: str
    started_timeout: Optional[float]
    finished_timeout: Optional[float]
