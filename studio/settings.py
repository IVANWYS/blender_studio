"""Django settings module.

All configuration is supplied via environment variables.
"""
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from typing import List
import os
import pathlib
import sys

from dotenv import load_dotenv
import braintree
import dj_database_url
import meilisearch

# Translation
from django.utils.translation import gettext_lazy as _

# Load variables from .env, if available
path = os.path.dirname(os.path.abspath(__file__)) + '/../.env'
print(path)
if os.path.isfile(path):
    load_dotenv(path)


def _get(name: str, default=None, coerse_to=None):
    val = os.environ.get(name, default)
    return coerse_to(val) if coerse_to is not None else val


BASE_DIR = pathlib.Path(__file__).absolute().parent.parent
TESTING = sys.argv[1:2] == ['test']

ADMIN_SITE_HEADER = 'Blender Studio Admin'
ADMIN_SITE_TITLE = 'Blender Studio'

# Application definition

INSTALLED_APPS = [
    # Translation
    'modeltranslation',
    'django.contrib.redirects',
    'django.contrib.flatpages',
    'emails',
    'blog',
    'comments',
    'common',
    'films',
    'search',
    'static_assets',
    'subscriptions',
    'training',
    'cloud_import',
    'stats',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'blender_id_oauth_client',
    'profiles',
    'looper',
    'pipeline',
    'sorl.thumbnail',
    'taggit',
    'actstream',
    'background_task',
    'users',
    'loginas',
    'nested_admin',
    'characters',
    'logentry_admin',
    'rest_framework',
    'rest_framework.authtoken',
    'source_upload',
    'payments',
    'import_export',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Translation
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'subscriptions.middleware.SetCurrencyMiddleware',
]

ROOT_URLCONF = 'studio.urls'

STATIC_URL = _get('STATIC_URL', '/static-studio/')
STATIC_ROOT = _get('STATIC_ROOT', BASE_DIR / 'public/static', str)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'public/media'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR / 'comments/templates'),
            str(BASE_DIR / 'common/templates'),
            str(BASE_DIR / 'films/templates'),
            str(BASE_DIR / 'search/templates'),
            str(BASE_DIR / 'training/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.search_client_config',
                'common.context_processors.settings_analytics_id',
                'common.context_processors.extra_context',
                'training.context_processors.enums',
                # TODO(anna) when Profile model is added, this should become a prop on it instead.
                'training.context_processors.favorited',
                'users.context_processors.user_dict',
                'looper.context_processors.preferred_currency',
                'loginas.context_processors.impersonated_session_status',
                # Translation
                'django.template.context_processors.i18n',
            ]
        },
    },
]

WSGI_APPLICATION = 'studio.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Blender ID login with Blender ID OAuth client

LOGIN_URL = '/oauth/login'
LOGOUT_URL = '/oauth/logout'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SESSION_COOKIE_AGE = 604_800 * 8  # 8 weeks (in seconds)

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en' #'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True # False

LANGUAGES = (
    ('en', _('English')),
    ('zh-hans', _('Simplified Chinese')),
    ('zh-hant', _('Traditional Chinese')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'
MODELTRANSLATION_AUTO_POPULATE = 'default'

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

DATE_FORMAT = 'N j, Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = f'{DATE_FORMAT} {TIME_FORMAT}'

USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 3

USE_TZ = True

PIPELINE = {
    'JS_COMPRESSOR': 'pipeline.compressors.jsmin.JSMinCompressor',
    'CSS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'JAVASCRIPT': {
        'studio': {
            'source_filenames': [
                'comments/scripts/*.js',
                'comments/scripts/components/*.js',
                'common/scripts/*.js',
            ],
            'output_filename': 'js/studio.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'training': {
            'source_filenames': [
                'training/scripts/section.js',
                'training/scripts/training.js',
                'training/scripts/components/card_training.js',
            ],
            'output_filename': 'js/training.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'search': {
            'source_filenames': ['search/scripts/*.js'],
            'output_filename': 'js/search.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'training_search': {
            'source_filenames': ['training/scripts/training_search.js'],
            'output_filename': 'js/training_search.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'film_search': {
            'source_filenames': ['films/scripts/film_search.js'],
            'output_filename': 'js/film_search.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'vendor': {
            'source_filenames': [
                'common/scripts/vendor/bootstrap.bundle.js',
                'common/scripts/vendor/plyr.polyfilled.js',
                'common/scripts/vendor/js.cookie.js',
                'common/scripts/vendor/imagesloaded.pkgd.js',
                'common/scripts/vendor/confetti.browser.min.js',
            ],
            'output_filename': 'js/vendor.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'vendor_instantsearch': {
            'source_filenames': [
                'common/scripts/vendor/instant-meilisearch.umd.min.js',
                'common/scripts/vendor/instantsearch.production.min.js',
            ],
            'output_filename': 'js/vendor_instantsearch.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'vendor_chartjs': {
            'source_filenames': ['common/scripts/vendor/chart.bundle.min.js'],
            'output_filename': 'js/vendor_chartjs.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'vendor_masonry': {
            'source_filenames': ['common/scripts/vendor/masonry.pkgd.js'],
            'output_filename': 'js/vendor_masonry.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'looper': {
            'source_filenames': [
                'looper/scripts/*.js',
            ],
            'output_filename': 'js/looper.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'subscriptions': {
            'source_filenames': [
                'common/scripts/ajax.js',
                'subscriptions/scripts/*.js',
            ],
            'output_filename': 'js/subscriptions.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'vendor_highlight': {
            'source_filenames': ['common/scripts/vendor/highlight.min.js'],
            'output_filename': 'js/vendor_highlight.js',
            'extra_context': {'async': False, 'defer': False},
        },
        'ajax': {
            'source_filenames': ['common/scripts/ajax.js'],
            'output_filename': 'js/ajax.js',
        },
    },
    'STYLESHEETS': {
        'studio': {
            'source_filenames': ('common/styles/studio/studio.scss',),
            'output_filename': 'css/studio.css',
            'extra_context': {'media': 'screen'},
        },
        'vendor_highlight': {
            'source_filenames': ('common/styles/vendor/highlight/monokai-sublime.min.css',),
            'output_filename': 'css/highlight-monokai-sublime.css',
            'extra_context': {'media': 'screen'},
        },
        'looper_admin': {
            'source_filenames': ('looper/styles/*.sass',),
            'output_filename': 'css/looper_admin.css',
            'extra_context': {'media': 'screen,projection'},
        },
    },
    'COMPILERS': ('libsasscompiler.LibSassCompiler',),
    'DISABLE_WRAPPER': True,
}

STATICFILES_STORAGE = 'pipeline.storage.PipelineManifestStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {'format': '%(asctime)-15s %(levelname)8s %(name)s %(message)s'},
        'verbose': {
            'format': '%(asctime)-15s %(levelname)8s %(name)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',  # Set to 'verbose' in production
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'asyncio': {'level': 'WARNING'},
        'django': {'level': 'WARNING'},
        'urllib3': {'level': 'WARNING'},
        'search': {'level': 'DEBUG'},
        'static_assets': {'level': 'DEBUG'},
    },
    'root': {'level': 'WARNING', 'handlers': ['console']},
}

SITE_ID = 1

# Required by Django Debug Toolbar
INTERNAL_IPS = ['127.0.0.1']


TAGGIT_CASE_INSENSITIVE = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
PUBLIC_FILE_STORAGE = 'common.storage.S3PublicStorage'
# Do not set "public-read" ACL on bucket items
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_S3_REGION_NAME = _get('AWS_S3_REGION_NAME')
AWS_STORAGE_BUCKET_NAME = _get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = _get('AWS_S3_CUSTOM_DOMAIN')
# Used for temporary storage when processing videos (and in the future
# when performing direct-to-s3 uploads). Once the upload is completed
# we take care of moving the file to AWS_STORAGE_BUCKET_NAME through a
# background task.
AWS_UPLOADS_BUCKET_NAME = _get('AWS_UPLOADS_BUCKET_NAME')
AWS_S3_OBJECT_PARAMETERS = {
    # Set max-age to 10 days
    'CacheControl': str('private,max-age=1728000'),
}
# In order to set the same headers for already existing S3 keys,
# --metadata-directive must be used, e.g.:
#       aws s3 cp s3://blender-studio/ s3://blender-studio/ --exclude "*" --include "*.jpg" \
#        --recursive --metadata-directive REPLACE --cache-control public,max-age=864000

THUMBNAIL_STORAGE = PUBLIC_FILE_STORAGE
THUMBNAIL_CROP_MODE = 'center'
THUMBNAIL_SIZE_S = '400x225'
THUMBNAIL_SIZE_M = '1280x720'

CSRF_COOKIE_NAME = 'bstudiocsrftoken'

ACTSTREAM_SETTINGS = {
    'MANAGER': 'users.managers.CustomStreamManager',
    'FETCH_RELATIONS': True,
}

ADMIN_MAIL = _get('ADMIN_MAIL', 'admin@studio')
STORE_PRODUCT_URL = _get('STORE_PRODUCT_URL')
STORE_MANAGE_URL = _get('STORE_MANAGE_URL')

SUPPORTED_CURRENCIES = {'EUR', 'USD'}

# Collection of automatically renewing subscriptions will be attempted this
# many times before giving up and setting the subscription status to 'on-hold'.
#
# This value is only used when automatic renewal fails, so setting it < 1 will
# be treated the same as 1 (one attempt is made, and failure is immediate, no
# retries).
LOOPER_CLOCK_MAX_AUTO_ATTEMPTS = 3

# Only retry collection of automatic renewals this long after the last failure.
# This separates the frequency of retrials from the frequency of the clock.
LOOPER_ORDER_RETRY_AFTER = relativedelta(days=2)

# The system user from looper/fixtures/systemuser.json. This user is required
# for logging things in the admin history (those log entries always need to
# have a non-NULL user ID).
LOOPER_SYSTEM_USER_ID = _get('LOOPER_SYSTEM_USER_ID', 1, int)

LOOPER_MONEY_LOCALE = 'en_US.UTF-8'

LOOPER_SUBSCRIPTION_CREATION_WARNING_THRESHOLD = relativedelta(days=1)

# Expire on-hold subscriptions after they haven't been paid for half a year
LOOPER_SUBSCRIPTION_EXPIRE_AFTER = timedelta(weeks=4 * 6)
LOOPER_ORDER_RECEIPT_PDF_URL = 'subscriptions:receipt-pdf'
LOOPER_PAY_EXISTING_ORDER_URL = 'subscriptions:pay-existing-order'
LOOPER_MANAGER_MAIL = ADMIN_MAIL
LOOPER_USER_SEARCH_FIELDS = ('user__full_name',)


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'PAGE_SIZE': 10,
}

if TESTING:
    STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
    AWS_STORAGE_BUCKET_NAME = 'blender-studio-test'
    MEILISEARCH_INDEX_UID = 'test_studio'
    TRAINING_INDEX_UID = 'test_training'
    LOGGING = {
        'version': 1,
        'loggers': {
            '': {'level': 'CRITICAL'},
        },
    }

SECRET_KEY = _get('SECRET_KEY')
DEBUG = _get('DEBUG', False, bool)
TEMPLATE_DEBUG = DEBUG
# Enable to use OAuth without https during local development
if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    TEMPLATE_STRING_IF_INVALID = 'DEBUG WARNING: undefined template variable [%s] not found'
    DEBUG_TOOLBAR_CONFIG = {
        'PROFILER_MAX_DEPTH': 20,
        'SQL_WARNING_THRESHOLD': 100,  # milliseconds
    }
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

ALLOWED_HOSTS: List[str] = _get('ALLOWED_HOSTS', '', str).split(',')
# ALLOWED_HOSTS: List[str] = ['studio.local']

BLENDER_ID = {
    # MUST end in a slash:
    # "BASE_URL": _get('BID_BASE_URL', "https://id.blender.org/"),
    "BASE_URL": _get('BID_BASE_URL'),
    "OAUTH_CLIENT": _get('BID_OAUTH_CLIENT'),
    "OAUTH_SECRET": _get('BID_OAUTH_SECRET'),
    "WEBHOOK_USER_MODIFIED_SECRET": (_get('BID_WEBHOOK_USER_MODIFIED_SECRET', '') or '').encode(),
    # Credentials linked to a Blender ID system cloud_badger user, for updating subscriber badges
    "BADGER_API_OAUTH_CLIENT": _get('BADGER_API_OAUTH_CLIENT'),
    "BADGER_API_OAUTH_SECRET": _get('BADGER_API_OAUTH_SECRET'),
    "BADGER_API_ACCESS_TOKEN": _get('BADGER_API_ACCESS_TOKEN'),
}

DEFAULT_DATABASE_URL = 'postgres://studio:studio@localhost:5432/studio_2'
DATABASES = {
    'default': dj_database_url.config(default=DEFAULT_DATABASE_URL),
}

# Braintree configuration
# Provide merchant accounts in the following format:
#   `CURRENCY_CODE:ACCOUNT_ID,CURRENCY_CODE:ACCOUNT_ID`
# where comma separates multiple merchant accounts
_BT_MERCHANT_ACCOUNTS = _get('BT_MERCHANT_ACCOUNTS', '', str)
BT_MERCHANT_ACCOUNTS = _BT_MERCHANT_ACCOUNTS.split(',') if _BT_MERCHANT_ACCOUNTS else []
BT_ENVIRONMENT = _get('BT_ENVIRONMENT', 'Sandbox')  # Sandbox or Production
GATEWAYS = {
    'braintree': {
        'environment': getattr(braintree.Environment, BT_ENVIRONMENT),
        'merchant_id': _get('BT_MERCHANT_ID'),
        'public_key': _get('BT_PUBLIC_KEY'),
        'private_key': _get('BT_PRIVATE_KEY'),
        'merchant_account_ids': dict(acc.split(':') for acc in BT_MERCHANT_ACCOUNTS),
        'supported_collection_methods': {'automatic', 'manual'},
    },
    'bank': {'supported_collection_methods': {'manual'}},
}

# Optional Sentry configuration

SENTRY_DSN = _get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=False,
        # Looks like IP address is also not sent when this is False.
    )

# Meilisearch configuration
MEILISEARCH_INDEX_UID = 'studio'
TRAINING_INDEX_UID = 'training'
MEILI_MASTER_KEY = _get('MEILI_MASTER_KEY')
MEILISEARCH_PUBLIC_KEY = _get('MEILISEARCH_PUBLIC_KEY')
MEILISEARCH_API_ADDRESS = _get('MEILISEARCH_API_ADDRESS')
SEARCH_CLIENT = meilisearch.Client(MEILISEARCH_API_ADDRESS, MEILI_MASTER_KEY)

DEFAULT_RANKING_RULES = [
    'typo',
    'words',
    'proximity',
    'attribute',
    'exactness',
]
DATE_DESC_RANKING_RULES = ['sort', 'timestamp:desc', *DEFAULT_RANKING_RULES]
DATE_ASC_RANKING_RULES = ['sort', 'timestamp:asc', *DEFAULT_RANKING_RULES]
MAIN_SEARCH = {
    'SEARCHABLE_ATTRIBUTES': [
        'model',
        'name',
        'film_title',
        'tags',
        'secondary_tags',
        'topic',
        'collection_name',
        'chapter_name',
        'description',
        'summary',
        'content',
        'author_name',
    ],
    'SORTABLE_ATTRIBUTES': [
        'timestamp',
        'date_created',
        'date_updated',
        'date_published',
    ],
    'FACETING_ATTRIBUTES': ['model', 'film_title', 'license', 'media_type', 'free'],
    'RANKING_RULES': {
        MEILISEARCH_INDEX_UID: DEFAULT_RANKING_RULES,
        f'{MEILISEARCH_INDEX_UID}_date_desc': DATE_DESC_RANKING_RULES,
        f'{MEILISEARCH_INDEX_UID}_date_asc': DATE_ASC_RANKING_RULES,
    },
}
TRAINING_SEARCH = {
    'SEARCHABLE_ATTRIBUTES': [
        'model',
        'name',
        'training_name',
        'tags',
        'secondary_tags',
        'chapter_name',
        'description',
        'summary',
        'author_name',
    ],
    'SORTABLE_ATTRIBUTES': [
        'timestamp',
        'date_created',
        'date_updated',
        'date_published',
    ],
    'FACETING_ATTRIBUTES': ['type', 'difficulty'],
    'RANKING_RULES': {
        TRAINING_INDEX_UID: DEFAULT_RANKING_RULES,
        f'{TRAINING_INDEX_UID}_date_desc': DATE_DESC_RANKING_RULES,
        f'{TRAINING_INDEX_UID}_date_asc': DATE_ASC_RANKING_RULES,
    },
}

# AWS configuration

AWS_ACCESS_KEY_ID = _get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = _get('AWS_SECRET_ACCESS_KEY')
AWS_CLOUDFRONT_KEY_ID = _get('AWS_CLOUDFRONT_KEY_ID')
if AWS_CLOUDFRONT_KEY_ID:
    with open(BASE_DIR / f'pk-{AWS_CLOUDFRONT_KEY_ID}.pem', 'rb') as f:
        AWS_CLOUDFRONT_KEY = f.read()

BLENDER_CLOUD_SECRET_KEY = _get('BLENDER_CLOUD_SECRET_KEY')
BLENDER_CLOUD_AUTH_ENABLED = _get('BLENDER_CLOUD_AUTH_ENABLED', False, bool)
BLENDER_CLOUD_DOMAIN = _get('BLENDER_CLOUD_DOMAIN')

COCONUT_API_KEY = _get('COCONUT_API_KEY')
COCONUT_DECLARED_HOSTNAME = _get('COCONUT_DECLARED_HOSTNAME')

if _get('DEFAULT_FROM_EMAIL'):
    DEFAULT_FROM_EMAIL = _get('DEFAULT_FROM_EMAIL')
MAILGUN_API_KEY = _get('MAILGUN_API_KEY')
MAILGUN_SENDER_DOMAIN = _get('MAILGUN_SENDER_DOMAIN')
NEWSLETTER_LIST = _get('NEWSLETTER_LIST')
NEWSLETTER_NONSUBSCRIBER_LIST = _get('NEWSLETTER_NONSUBSCRIBER_LIST')
NEWSLETTER_SUBSCRIBER_LIST = _get('NEWSLETTER_SUBSCRIBER_LIST')
# By default, dump emails to the console instead of trying to actually send them.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
if MAILGUN_SENDER_DOMAIN:
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL = {
        "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN,
        "MAILGUN_WEBHOOK_SIGNING_KEY": _get('MAILGUN_WEBHOOK_SIGNING_KEY'),
        'WEBHOOK_SECRET': _get('MAILGUN_WEBHOOK_SECRET'),
    }

GEOIP2_DB = _get('GEOIP2_DB')

GOOGLE_ANALYTICS_TRACKING_ID = _get('GOOGLE_ANALYTICS_TRACKING_ID')
GOOGLE_RECAPTCHA_SECRET_KEY = _get('GOOGLE_RECAPTCHA_SECRET_KEY')
GOOGLE_RECAPTCHA_SITE_KEY = _get('GOOGLE_RECAPTCHA_SITE_KEY')


# # Default: 1000
# DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# # Default: 100
# DATA_UPLOAD_MAX_NUMBER_FILES = None

# FILE_UPLOAD_MAX_MEMORY_SIZE = 3000000000


# # Stripe Test Mode
STRIPE_PUBLISHABLE_KEY = _get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = _get('STRIPE_SECRET_KEY')
STRIPE_ENDPOINT_SECRET = _get('STRIPE_ENDPOINT_SECRET')
PRODUCT_PRICE_1_MONTH = _get('PRODUCT_PRICE_1_MONTH')
PRODUCT_PRICE_3_MONTH = _get('PRODUCT_PRICE_3_MONTH')
PRODUCT_PRICE_6_MONTH = _get('PRODUCT_PRICE_6_MONTH')
PRODUCT_PRICE_1_YEAR = _get('PRODUCT_PRICE_1_YEAR')