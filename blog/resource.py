from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ManyToManyWidget
from import_export.widgets import BooleanWidget
from blog.models import Post
from films.models.films import Film
from time import time
import datetime
from django.contrib.auth import get_user_model
User = get_user_model()

class CheckBooleanWidget(BooleanWidget):

    def render(self, value, obj):
        if value in self.NULL_VALUES:
            return "Unknown"
        return 'Yes' if value else 'NO'
    
    def clean(self, value, row, *args, **kwargs):
        if value in self.NULL_VALUES:
            return None
        return True if value in ['Yes','是','Y'] else False
    

class PostResource(resources.ModelResource):
    title = Field(column_name='title', attribute='title')
    slug = Field(column_name='slug', attribute='slug')
    content = Field(column_name='content', attribute='content')
    is_published = Field(column_name='is_published', attribute='is_published', widget=CheckBooleanWidget())
    author = Field(column_name='author', attribute='author', widget=ForeignKeyWidget(User, field='username'))
    film = Field(column_name='film', attribute='film', widget=ForeignKeyWidget(Film, field='slug'))

    
    class Meta:
        model = Post
        #fields = ('name', 'chapter_name')
        exclude = ['id', 'comments', 'date_updated']
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
