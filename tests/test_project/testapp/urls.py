from django.conf.urls.defaults import *
from testapp.handlers import EchoHandler, PlaceHandler
from topsoil.resources import BaseResource

echo = BaseResource(EchoHandler)
places = BaseResource(PlaceHandler)

urlpatterns = patterns('',
    url(r'^echo(\.(?P<emitter_format>.+))?$', echo),
    url(r'^places(\.(?P<emitter_format>.+))?$', places),
    url(r'^places/(?P<place_id>\d+)(\.(?P<emitter_format>.+))?$', places),
    url(r'^places/(?P<method>add)(\.(?P<emitter_format>.+))?$', places),
        url(r'^places/(?P<place_id>\d+)/(?P<method>edit)(\.(?P<emitter_format>.+))?$', places),
)
