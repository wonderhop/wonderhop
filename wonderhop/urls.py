from django.conf.urls.defaults import *
from django.conf import settings

if settings.LANDING_PAGE:
    urlpatterns = patterns('',
        (r'', include('wonderhop.landing.urls')),
    )
else:
    urlpatterns = patterns('',
        # When developing for the non-landing page site,
        # put includes to new Django apps here.
    )

from django.contrib import admin
admin.autodiscover()
urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
