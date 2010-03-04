from django.conf.urls.defaults import *

urlpatterns = patterns('oauth_clients.views',
    url(r'^$', 'oauth_applications'),
    url(r'^new$', 'oauth_application_add'),
    url(r'^(?P<application_id>\d+)$', 'oauth_application_details'),
    url(r'^(?P<application_id>\d+)/edit$', 'oauth_application_edit'),
    url(r'^(?P<application_id>\d+)/reset_key$', 'oauth_application_reset_key'),
)
