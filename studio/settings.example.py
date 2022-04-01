import os
from typing import List

# Enable to use OAuth without https during local development
import braintree
import meilisearch
from dateutil.relativedelta import relativedelta

from studio.settings_common import *

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SECRET_KEY = 'CHANGE_ME'
DEBUG = True
ALLOWED_HOSTS: List[str] = ['studio.local']

BLENDER_ID = {
    # MUST end in a slash:
    "BASE_URL": "http://id.local:8000/",
    "OAUTH_CLIENT": "CHANGE_ME",
    "OAUTH_SECRET": "CHANGE_ME",
    "WEBHOOK_USER_MODIFIED_SECRET": b"CHANGE_ME",
    # Credentials linked to a Blender ID system cloud_badger user, for updating subscriber badges
    "BADGER_API_OAUTH_CLIENT": "CHANGE_ME",
    "BADGER_API_OAUTH_SECRET": "CHANGE_ME",
    "BADGER_API_ACCESS_TOKEN": "CHANGE_ME",
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'studio',
        'USER': 'studio',
        'PASSWORD': 'CHANGE_ME',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

GATEWAYS = {
    'braintree': {
        'environment': braintree.Environment.Sandbox,
        'merchant_id': 'CHANGE_ME',
        'public_key': 'CHANGE_ME',
        'private_key': 'CHANGE_ME',
        # Merchant Account IDs for different currencies.
        # Configured in Braintree: Account → Merchant Account Info.
        'merchant_account_ids': {'EUR': 'CHANGE_ME', 'USD': 'CHANGE_ME'},
        # Blender Studio allows both automatic and manual collection with Braintree:
        'supported_collection_methods': {'automatic', 'manual'},
    },
    'bank': {
        'supported_collection_methods': {'manual'},
    },
}

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
LOOPER_SYSTEM_USER_ID = 1

# Convertion rates from the given rate to euros.
# This allows us to express the foreign currency in €.
LOOPER_CONVERTION_RATES_FROM_EURO = {
    'EUR': 1.0,
    'USD': 1.15,
}

LOOPER_MONEY_LOCALE = 'en_US.UTF-8'

SUPPORTED_CURRENCIES = {'EUR', 'USD'}

# Get the latest from https://dev.maxmind.com/geoip/geoip2/geolite2/. Note that you should check
# whether we are allowed to redistribute the file according to the new license (per 2020) if you
# want to check the file into the repository.
GEOIP2_DB = 'CHANGE-ME/GeoLite2-Country.mmdb'

GOOGLE_RECAPTCHA_SITE_KEY = 'CHANGE_ME'
GOOGLE_RECAPTCHA_SECRET_KEY = 'CHANGE_ME'

MEILISEARCH_PUBLIC_KEY = 'CHANGE_ME'
MEILISEARCH_PRIVATE_KEY = 'CHANGE_ME'
# Change the address to 'https://studio.blender.org/s/' in production
MEILISEARCH_API_ADDRESS = 'http://127.0.0.1:7700/'
SEARCH_CLIENT = meilisearch.Client(MEILISEARCH_API_ADDRESS, MEILISEARCH_PRIVATE_KEY)

AWS_ACCESS_KEY_ID = 'CHANGE_ME'
AWS_SECRET_ACCESS_KEY = 'CHANGE_ME'
AWS_CLOUDFRONT_KEY_ID = os.environ.get('AWS_CLOUDFRONT_KEY_ID')
AWS_CLOUDFRONT_KEY = os.environ.get('AWS_CLOUDFRONT_KEY').encode('ascii')

GOOGLE_ANALYTICS_TRACKING_ID = ''
GOOGLE_RECAPTCHA_SITE_KEY = ''
GOOGLE_RECAPTCHA_SECRET_KEY = ''

# Coconut API. See https://app.coconut.co/settings/api
COCONUT_API_KEY = ''
# The hostname used by Coconut to push updates to (via webhooks)
COCONUT_DECLARED_HOSTNAME = ''

# Mailgun API.
# See https://documentation.mailgun.com/en/latest/api-intro.html#authentication
MAILGUN_SENDER_DOMAIN = 'CHANGE_ME'
MAILGUN_API_KEY = 'CHANGE_ME'
MAILGUN_WEBHOOK_SIGNING_KEY = 'CHANGE_ME'
# Uncomment this if you want to use an email backend
# EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
ANYMAIL = {
    'MAILGUN_SENDER_DOMAIN': MAILGUN_SENDER_DOMAIN,
    'MAILGUN_WEBHOOK_SIGNING_KEY': 'CHANGE_ME',
    'WEBHOOK_SECRET': 'CHANGE_ME:CHANGE_ME',
}

INSTALLED_APPS += [
    'sslserver',
]
