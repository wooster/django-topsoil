from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('test_provider.testapp.urls')),
    url(r'^oauth_clients/', include('test_provider.oauth_clients.urls')),
    url(r'^oauth/authenticate/', 'test_provider.oauth_clients.views.oauth_authenticate'),
    url(r'^oauth/authorize/', 'test_provider.oauth_clients.views.oauth_authorize_wrapper'),
    url(r'^oauth/', include('oauth_provider.urls')),
)

urlpatterns += patterns('testapp.views',
    url(r'^$', 'test_index'),
)

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'test_provider.testapp.resources.logout'),
    url(r'^', include('test_provider.testapp.urls')),
)
