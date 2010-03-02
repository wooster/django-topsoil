from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^api/', include('test_project.testapp.urls')),
)

urlpatterns += patterns('testapp.views',
    url(r'^$', 'test_index'),
)

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'test_project.testapp.resources.logout'),
    url(r'^', include('test_project.testapp.urls')),
)
