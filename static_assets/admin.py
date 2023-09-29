from django.contrib import admin
import nested_admin

from looper.admin.filters import ChoicesFieldListWithEmptyFilter

from common.mixins import AdminUserDefaultMixin
from static_assets.models import static_assets, licenses, m3u8_assets

# Data import export
from .resource import StaticAssetResource, VideoResource, VideoTrackResource

from import_export.admin import ImportExportModelAdmin

@admin.register(licenses.License)
class LicenseAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class ImageInline(nested_admin.NestedTabularInline):
    model = static_assets.Image
    show_change_link = True
    extra = 0
    max_num = 1


class VideoVariationInline(nested_admin.NestedTabularInline):
    model = static_assets.VideoVariation
    show_change_link = True
    extra = 0


class VideoTrackInline(nested_admin.NestedTabularInline):
    model = static_assets.VideoTrack
    show_change_link = True
    extra = 0


class VideoInline(nested_admin.NestedTabularInline):
    model = static_assets.Video
    inlines = [VideoVariationInline, VideoTrackInline]
    show_change_link = True
    extra = 0
    readonly_fields = ['play_count']


@admin.register(static_assets.StaticAsset)
class StaticAssetAdmin(ImportExportModelAdmin, AdminUserDefaultMixin, nested_admin.NestedModelAdmin):
    actions = ['process_videos', 'transcribe_videos']
    inlines = [ImageInline, VideoInline]
    autocomplete_fields = ['user', 'author', 'contributors']
    list_display = [
        '__str__',
        'date_created',
        'date_updated',
        'has_tracks',
        'view_count',
        'download_count',
    ]
    fieldsets = (
        (
            None,
            {
                'fields': [
                    'id',
                    'source',
                    'original_filename',
                    'size_bytes',
                    ('source_type', 'content_type'),
                    ('user', 'author', 'contributors'),
                    'license',
                    'thumbnail',
                    ('slug', 'date_created', 'view_count', 'download_count'),
                ],
            },
        ),
        (
            'If you are uploading an image or a video',
            {
                'fields': (),
                'description': 'The fields below depend on the source type of the uploaded '
                'asset. Add an <strong>Image</strong> if you are uploading an '
                'image, or a <strong>Video</strong> for video uploads.',
            },
        ),
    )
    list_filter = [
        'source_type',
        'section__chapter__training',
        'assets__film',
        'assets__category',
        ('video__tracks__language', ChoicesFieldListWithEmptyFilter),
    ]
    search_fields = [
        'source',
        'original_filename',
        'user__first_name',
        'user__last_name',
        'author__first_name',
        'author__last_name',
        'id',
        'source_type',
        'section__name',
        'assets__name',
    ]
    readonly_fields = [
        'original_filename',
        'size_bytes',
        'date_created',
        'id',
        'view_count',
        'download_count',
        'slug',
    ]

    def process_videos(self, request, queryset):
        """For each asset, process all videos attached if available."""
        videos_processing_count = 0
        for a in queryset:
            a.process_video()
            videos_processing_count += 1
        if videos_processing_count == 0:
            message_bit = "No video is"
        elif videos_processing_count == 1:
            message_bit = "1 video is"
        else:
            message_bit = "%s videos are" % videos_processing_count
        self.message_user(request, "%s processing." % message_bit)

    process_videos.short_description = "Process videos for selected assets"

    def transcribe_videos(self, request, queryset):
        """For each asset, transcribe all videos attached if available."""
        videos_transcribing_count = 0
        for a in queryset:
            a.transcribe_video()
            videos_transcribing_count += 1
        if videos_transcribing_count == 0:
            message_bit = "No video is"
        elif videos_transcribing_count == 1:
            message_bit = "1 video is"
        else:
            message_bit = "%s videos are" % videos_transcribing_count
        self.message_user(request, "%s transcribing." % message_bit)

    transcribe_videos.short_description = "Transcribe videos for selected assets"

    def has_tracks(self, obj):
        """Display yes/no icon indicating that this is a video with tracks.

        Checks if track files actually exist in storage (e.g. by calling AWS S3).
        """
        if obj.video is None:
            return None
        return any(
            track.source.storage.exists(track.source.name) for track in obj.video.tracks.all()
        )

    has_tracks.boolean = True

    resource_class = StaticAssetResource

@admin.register(static_assets.Video)
class VideoAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    list_display = ('id', 'duration', 'static_asset_id')
    list_display_links = ('id', 'duration', 'static_asset_id')

    resource_class = VideoResource


@admin.register(static_assets.VideoTrack)
class VideoTrackAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    list_display = ('id', 'video', 'language')
    readonly_fields = ['video']

    resource_class = VideoTrackResource


@admin.register(m3u8_assets.M3u8Playlist)
class M3u8PlaylistAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'source', 'types', 'sVideo')
    list_display_links = ('id', 'title')
    readonly_fields=('slug',)
    search_fields = ('title', 'types', 'sVideo')
    list_per_page = 25


@admin.register(m3u8_assets.M3u8Source)
class M3u8SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'source', 'types')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'types')
    list_per_page = 25
