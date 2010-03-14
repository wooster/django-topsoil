from django.conf.urls.defaults import *

urlpatterns = patterns('places.views',
    (r'^$', 'places_all'),
    (r'^/add$', 'places_add'),
)
