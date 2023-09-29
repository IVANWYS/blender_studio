from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ManyToManyWidget
from import_export.widgets import BooleanWidget
from static_assets.models.static_assets import StaticAsset
from characters.models import Character, CharacterVersion, CharacterShowcase
from films.models.films import Film
from time import time
import datetime


class CheckBooleanWidget(BooleanWidget):

    def render(self, value, obj):
        if value in self.NULL_VALUES:
            return "Unknown"
        return 'Yes' if value else 'NO'
    
    def clean(self, value, row, *args, **kwargs):
        if value in self.NULL_VALUES:
            return None
        return True if value in ['Yes','是','Y'] else False
    
        

class CharacterResource(resources.ModelResource):
    slug = Field(column_name='slug', attribute='slug')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    film = Field(column_name='film', attribute='film', widget=ForeignKeyWidget(Film, field='slug'))


    class Meta:
        model = Character
        #fields = ('name', 'chapter_name')
        exclude = ['id', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True


class CharacterVersionResource(resources.ModelResource):
    description = Field(column_name='description', attribute='description')
    character = Field(column_name='character', attribute='character', widget=ForeignKeyWidget(Character, field='slug'))
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    is_free = Field(column_name='is_free', attribute='is_free', widget=CheckBooleanWidget())
    static_asset = Field(column_name='static_asset', attribute='static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))
    preview_video_static_asset = Field(column_name='preview_video_static_asset', attribute='preview_video_static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))

    class Meta:
        model = CharacterVersion
        #fields = ('name', 'chapter_name')
        exclude = ['date_updated']
        import_id_fields = ['id']
        skip_unchanged = True
        report_skipped = True


class CharacterShowcaseResource(resources.ModelResource):
    title = Field(column_name='title', attribute='title')
    character = Field(column_name='character', attribute='character', widget=ForeignKeyWidget(Character, field='slug'))
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    is_free = Field(column_name='is_free', attribute='is_free', widget=CheckBooleanWidget())
    static_asset = Field(column_name='static_asset', attribute='static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))
    preview_video_static_asset = Field(column_name='preview_video_static_asset', attribute='preview_video_static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))

    class Meta:
        model = CharacterShowcase
        #fields = ('name', 'chapter_name')
        exclude = ['date_updated']
        import_id_fields = ['id']
        skip_unchanged = True
        report_skipped = True
