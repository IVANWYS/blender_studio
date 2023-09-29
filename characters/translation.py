from modeltranslation.translator import translator, TranslationOptions
from .models import Character, CharacterVersion, CharacterShowcase


class CharacterTranslationOptions(TranslationOptions):
    fields = ['name']


translator.register(Character, CharacterTranslationOptions)


class CharacterVersionTranslationOptions(TranslationOptions):
    fields = ['description']


translator.register(CharacterVersion, CharacterVersionTranslationOptions)


class CharacterShowcaseTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


translator.register(CharacterShowcase, CharacterShowcaseTranslationOptions)
