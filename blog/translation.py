from modeltranslation.translator import translator, TranslationOptions
from .models import Post


class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'content_html', )


translator.register(Post, PostTranslationOptions)
