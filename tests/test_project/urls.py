from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('test_project.testapp.urls')),
    url(r'^oauth_clients/', include('test_project.oauth_clients.urls')),
    url(r'^oauth/', include('oauth_provider.urls')),
)

urlpatterns += patterns('testapp.views',
    url(r'^$', 'test_index'),
)

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'test_project.testapp.resources.logout'),
    url(r'^', include('test_project.testapp.urls')),
)
