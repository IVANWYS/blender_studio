from modeltranslation.translator import translator, TranslationOptions
from .models import Film, Collection, Asset


class FilmsTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'summary')


translator.register(Film, FilmsTranslationOptions)


class CollectionsTranslationOptions(TranslationOptions):
    fields = ('name', 'text')


translator.register(Collection, CollectionsTranslationOptions)


class AssetsTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


translator.register(Asset, AssetsTranslationOptions)
