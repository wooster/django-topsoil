import os
import sys

dirname = os.path.dirname(globals()["__file__"])
sys.path.insert(1, os.path.join(dirname, "..", ".."))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/topsoil.db'

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'su)wa0!bv=-=l_ib+p(c%#d%(&ow@otnl*=mfb3)zs0%h0tm1k'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'topsoil.middleware.ApiCsrfExemptionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    'topsoil.middleware.ApiOauthMiddleware',
)

ROOT_URLCONF = 'test_project.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates')
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'testapp',
    'oauth_clients',
    'oauth_provider',
    'topsoil',
)

OAUTH_AUTHORIZE_VIEW = 'oauth_clients.views.oauth_authorize'
