import os

from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG') != 'True'

ALLOWED_HOSTS = []

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

include(
    'components/database.py',
    'components/auth_password_validators.py',
    'components/installed_apps.py',
    'components/middleware.py',
    'components/templates.py',
    'components/internationalization.py'
)

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
