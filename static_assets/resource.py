from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import BooleanWidget
from .models.static_assets import StaticAsset, Video, VideoTrack
from .models.licenses import License
from django.contrib.auth import get_user_model
User = get_user_model()
from time import time


class CheckBooleanWidget(BooleanWidget):

    def render(self, value, obj):
        if value in self.NULL_VALUES:
            return "Unknown"
        return 'Yes' if value else 'NO'
    
    def clean(self, value, row, *args, **kwargs):
        if value in self.NULL_VALUES:
            return None
        return True if value in ['Yes','是','Y'] else False


class StaticAssetResource(resources.ModelResource):

    slug = Field(column_name='slug', attribute='slug')
    user = Field(column_name='user', attribute='user', widget=ForeignKeyWidget(User, field='username'))
    license = Field(column_name='license', attribute='license', widget=ForeignKeyWidget(License, field='slug'))

    # Create slug
    # def before_import_row(self, row, **kwargs):
    #     if row['slug'] == "":
    #         row['slug'] = hex(int(time() * 10000000))[2:]
            
    class Meta:
        model = StaticAsset
        exclude = ['id', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True


class VideoResource(resources.ModelResource):
    slug = Field(column_name='slug', attribute='slug')
    static_asset = Field(column_name='static_asset', attribute='static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))

    class Meta:
        model = Video
        exclude = ['id']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True

class VideoTrackResource(resources.ModelResource):
    slug = Field(column_name='slug', attribute='slug')
    video = Field(column_name='video', attribute='video', widget=ForeignKeyWidget(Video, field='slug'))

    class Meta:
        model = VideoTrack
        exclude = ['id']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
