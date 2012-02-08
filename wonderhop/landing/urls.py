from django.conf.urls.defaults import *

urlpatterns = patterns('wonderhop.landing.views',
    url(r'^$', 'home', name='home'),
    url(r'^thanks/$', 'thanks', name='thanks'),
)
