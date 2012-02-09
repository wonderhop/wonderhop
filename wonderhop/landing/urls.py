from django.conf.urls.defaults import *
from wonderhop.landing import views

urlpatterns = patterns("wonderhop.landing.views",
    url(r"^$", views.home),
    url(r"^about/$", views.about),
    url(r"^privacy/$", views.privacy),
    url(r"^jobs/$", views.jobs),
    url(r"^welcome/(\d+)/$", views.welcome),
    url(r"^r/(\w+)$", views.refer),
)
