import os
import dj_database_url
from .settings import *


ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME'), '*']
CSRF_TRUSTED_ORIGINS = ['https://'+os.environ.get('RENDER_EXTERNAL_HOSTNAME')] if os.environ.get('RENDER_EXTERNAL_HOSTNAME') else []

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'https://local-storess.onrender.com',
]


STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'raw_media': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'), 
        conn_max_age=0,
        ssl_require=True
    )
}

import cloudinary
if 'CLOUDINARY_URL' in os.environ:
    INSTALLED_APPS += ['cloudinary', 'cloudinary_storage']
    STORAGES['default'] = {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    }
    STORAGES['raw_media'] = {
        'BACKEND': 'cloudinary_storage.storage.RawMediaCloudinaryStorage',
    }
    # Initialize cloudinary configuration from the URL
    cloudinary.config(
        secure=True
    )