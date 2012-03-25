from django.conf.urls.defaults import *
from wonderhop.landing import views

urlpatterns = patterns("wonderhop.landing.views",
    url(r"^$", views.home),
    url(r"^login/$", views.login),
    url(r"^about/$", views.about),
    url(r"^privacy/$", views.privacy),
    url(r"^jobs/$", views.jobs),
    url(r"^wreath/$", views.wreath),
    url(r"^explanation/(\d+)/$", views.explanation),
    url(r"^welcome/(\d+)/$", views.welcome),
    url(r"^welcome/(\d+)/email/$", views.share_email),
    url(r"^r/(\w+)$", views.refer, name="refer"),
    url(r"^a/([^/]+)/?$", views.advertisement_landing),
)
