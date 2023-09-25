from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ManyToManyWidget
from import_export.widgets import BooleanWidget
from .models.films import Film
from .models.collections import Collection
from .models.assets import Asset
from static_assets.models.static_assets import StaticAsset


class CheckBooleanWidget(BooleanWidget):

    def render(self, value, obj):
        if value in self.NULL_VALUES:
            return "Unknown"
        return 'Yes' if value else 'NO'
    
    def clean(self, value, row, *args, **kwargs):
        if value in self.NULL_VALUES:
            return None
        return True if value in ['Yes','是','Y'] else False
    

class FilmResource(resources.ModelResource):
    title = Field(column_name='title', attribute='title')
    slug = Field(column_name='slug', attribute='slug')
    description = Field(column_name='description', attribute='description')
    summary = Field(column_name='summary', attribute='summary')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    is_featured = Field(column_name='is_featured', attribute='is_featured', widget=CheckBooleanWidget())
    show_production_logs_nav_link = Field(column_name='Show production logs nav link', attribute='show_production_logs_nav_link', widget=CheckBooleanWidget())
    show_production_logs_as_featured = Field(column_name='Show production logs as featured', attribute='show_production_logs_as_featured', widget=CheckBooleanWidget())
    show_blog_posts = Field(column_name='Show blog posts', attribute='show_blog_posts', widget=CheckBooleanWidget())
    show_landing_page = Field(column_name='Show landing page', attribute='show_landing_page', widget=CheckBooleanWidget())
    
    class Meta:
        model = Film
        exclude = ['id', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True


class CollectionResource(resources.ModelResource):
    name = Field(column_name='name', attribute='name')
    slug = Field(column_name='slug', attribute='slug')
    text = Field(column_name='text', attribute='text')
    film = Field(column_name='film', attribute='film', widget=ForeignKeyWidget(Film, field='slug'))
    parent = Field(column_name='parent', attribute='parent', widget=ForeignKeyWidget(Collection, field='slug'))


    class Meta:
        model = Collection
        exclude = ['id', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
        


class AssetResource(resources.ModelResource):
    name = Field(column_name='name', attribute='name')
    slug = Field(column_name='slug', attribute='slug')
    description = Field(column_name='description', attribute='description')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    is_featured = Field(column_name='is_featured', attribute='is_featured', widget=CheckBooleanWidget())
    is_free = Field(column_name='is_free', attribute='is_free', widget=CheckBooleanWidget())
    is_spoiler = Field(column_name='is_spoiler', attribute='is_spoiler', widget=CheckBooleanWidget())
    contains_blend_file = Field(column_name='contains_blend_file', attribute='contains_blend_file', widget=CheckBooleanWidget())
    film = Field(column_name='film', attribute='film', widget=ForeignKeyWidget(Film, field='slug'))
    collection = Field(column_name='collection', attribute='collection', widget=ForeignKeyWidget(Collection, field='slug'))
    static_asset = Field(column_name='static_asset', attribute='static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))

    
    class Meta:
        model = Asset
        exclude = ['id', 'tags', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
        
