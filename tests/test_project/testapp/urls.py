from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from topsoil.utils import FORMAT_PATTERN

#!! Should be fixtures:
try:
    test_user = User.objects.get(username='test')
except User.DoesNotExist:
    test_user = User.objects.create_user('test', 'test@example.com', 'test')
    test_user.is_superuser = True
    test_user.save()

urlpatterns = patterns('testapp.resources',
    url(r'^echo%s$' % FORMAT_PATTERN, 'echo'),
    url(r'^places%s$' % FORMAT_PATTERN, 'place_list'),
    url(r'^places/(?P<place_id>\d+)%s$' % FORMAT_PATTERN, 'place'),
    url(r'^places/add%s$' % FORMAT_PATTERN, 'place_add'),
    url(r'^places/(?P<place_id>\d+)/edit%s$' % FORMAT_PATTERN, 'place_edit'),
)
