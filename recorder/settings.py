import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '(m)5j4w0vs-*1=z47uq)_cfytv75z48daq=brn*=oo_d1@^b@e'
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []
SESSION_ENGINE = 'django.contrib.sessions.backends.file'

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recorder'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'recorder.urls'
WSGI_APPLICATION = 'recorder.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

DATABASES = {}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

RTMP_CONTROL_HOST = 'http://127.0.0.1:8111'
RTMP_SERVER = 'rtmp://127.0.0.1:2935/my_videos'
