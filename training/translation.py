from modeltranslation.translator import translator, TranslationOptions
from .models import Training, Chapter, Section


class TrainingsTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'summary')


translator.register(Training, TrainingsTranslationOptions)


class ChaptersTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


translator.register(Chapter, ChaptersTranslationOptions)


class SectionsTranslationOptions(TranslationOptions):
    fields = ('name', 'text')


translator.register(Section, SectionsTranslationOptions)
