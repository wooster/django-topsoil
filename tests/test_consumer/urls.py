from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('client.views',
    url(r'^$', 'index'),
    (r'^login$', 'places_signin'),
    (r'^logout$', 'places_signout'),
    (r'^return$', 'places_return'),
)
