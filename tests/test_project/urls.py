from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^api/', include('test_project.testapp.urls')),
)

urlpatterns += patterns('testapp.views',
    url(r'^$', 'test_index'),
)

urlpatterns += patterns('',
    url(r'^', include('test_project.testapp.urls')),
)
