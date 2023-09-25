from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ManyToManyWidget
from import_export.widgets import BooleanWidget
from static_assets.models.static_assets import StaticAsset
from .models.trainings import Training
from .models.chapters import Chapter
from .models.sections import Section


class CheckBooleanWidget(BooleanWidget):

    def render(self, value, obj):
        if value in self.NULL_VALUES:
            return "Unknown"
        return 'Yes' if value else 'NO'
    
    def clean(self, value, row, *args, **kwargs):
        if value in self.NULL_VALUES:
            return None
        return True if value in ['Yes','是','Y'] else False
    

class TrainingResource(resources.ModelResource):
    name = Field(column_name='name', attribute='name')
    slug = Field(column_name='slug', attribute='slug')
    description = Field(column_name='description', attribute='description')
    summary = Field(column_name='summary', attribute='summary')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    is_featured = Field(column_name='is_featured', attribute='is_featured', widget=CheckBooleanWidget())

    class Meta:
        model = Training
        exclude = ['id', 'tags', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True


class ChapterResource(resources.ModelResource):
    name = Field(column_name='name', attribute='name')
    slug = Field(column_name='slug', attribute='slug')
    description = Field(column_name='description', attribute='description')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    training = Field(column_name='training', attribute='training', widget=ForeignKeyWidget(Training, field='slug'))

    class Meta:
        model = Chapter
        exclude = ['id', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True


class SectionResource(resources.ModelResource):
    name = Field(column_name='name', attribute='name')
    slug = Field(column_name='slug', attribute='slug')
    text = Field(column_name='text', attribute='text')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    is_featured = Field(column_name='is_featured', attribute='is_featured', widget=CheckBooleanWidget())
    is_free = Field(column_name='is_free', attribute='is_free', widget=CheckBooleanWidget())
    chapter = Field(column_name='chapter', attribute='chapter', widget=ForeignKeyWidget(Chapter, field='slug'))
    static_asset = Field(column_name='static_asset', attribute='static_asset', widget=ForeignKeyWidget(StaticAsset, field='slug'))

    class Meta:
        model = Section
        exclude = ['id', 'tags', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
