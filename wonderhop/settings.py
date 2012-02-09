# Django settings for wonderhop project.
import os
PROJECT_DIR = os.path.dirname(__file__)

ADMINS = (
    ("Adam Ernst", "adamernst@cosmicsoft.net"),
)

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

LANDING_PAGE = False

STATIC_URL = "/static/"
STATIC_ROOT = ""
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "static"),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "wonderhop.sqlite",
    }
}

# Make this unique, and don"t share it with anybody.
SECRET_KEY = "k5198u4y2)$%2(p4k6*rkj3kdge03qba@&(9@f$zk_+1k__w^z"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.static",
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, "templates"),
)

ROOT_URLCONF = "wonderhop.urls"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "south",
    "wonderhop.landing",
)

try:
    from local_settings import *
except ImportError:
    pass
