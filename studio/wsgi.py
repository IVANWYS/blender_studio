"""
WSGI config for training project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import os.path
import pathlib

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).absolute().parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studio.settings')

# Load variables from .env, if available
path = BASE_DIR / '.env'
if os.path.isfile(path):
    load_dotenv(path)

application = get_wsgi_application()
