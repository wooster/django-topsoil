from django.contrib.auth import logout as logout_auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.middleware.csrf import get_token
from topsoil.decorators import resource
from topsoil.exceptions import HttpResponseException
from models import Place
from forms import PlaceForm

@resource()
def echo(request, format=None):
    metadata = {}
    data = {}
    if format == 'html':
        metadata['template'] = 'echo/echo.html'
    if format in ('html',):# 'rss', 'atom'):
        data['title'] = 'Echo'
    data['msg'] = request.GET.get('msg', '')
    return (metadata, data)

@login_required
@resource()
def verify_credentials(request):
    metadata = {}
    data = {}
    data['user'] = request.user
    return (metadata, data)

@resource()
def place(request, place_id, format=None):
    metadata = {}
    data = {}
    place = Place.objects.get(id=int(place_id))
    data['place'] = place
    if format == 'html':
        metadata['template'] = 'places/place.html'
        data['title'] = place.name
    return (metadata, data)

@resource()
def place_list(request, format=None, *args, **kwargs):
    metadata = {}
    data = {}
    data['places'] = Place.objects.all()
    data['title'] = 'All Places'
    if format == 'html':
        metadata['template'] = 'places/list.html'
    return (metadata, data)

@login_required
@resource()
def place_add(request, format=None, *args, **kwargs):
    metadata = {}
    data = {}
    if format == 'html':
        metadata['template'] = 'places/add.html'
    request_method = request.method.upper()
    if request_method == 'GET':
        data['form'] = PlaceForm()
    elif request_method == 'POST':
        form = PlaceForm(request.POST)
        try:
            place = form.save()
            if format == 'html':
                raise HttpResponseException(HttpResponseRedirect(request.GET.get('next_page') or place.get_absolute_url()))
            else:
                data['place'] = place
        except ValueError:
            data['form'] = form
    return (metadata, data)

@login_required
@resource()
def place_edit(request, format=None, *args, **kwargs):
    metadata = {}
    data = {}
    place_id = kwargs.get('place_id')
    request_method = request.method.upper()
    place = Place.objects.get(id=int(place_id))
    if format == 'html':
        metadata['template'] = 'places/edit.html'
    if request_method == 'GET':
        data['form'] = PlaceForm(instance=place)
    elif request_method == 'POST':
        form = PlaceForm(request.POST, instance=place)
        try:
            place = form.save()
            if format == 'html':
                raise HttpResponseException(HttpResponseRedirect(request.GET.get('next_page') or place.get_absolute_url()))
            else:
                data['place'] = place
        except ValueError:
            data['form'] = form
    return (metadata, data)

@resource()
def logout(request, format=None):
    metadata = {}
    data = {}
    #!! Awful, horrible.
    token = get_token(request)
    if token == request.GET.get('csrf_token', None):
        logout_auth(request)
        data['message'] = 'Logout successful.'
        if format == 'html':
            raise HttpResponseException(HttpResponseRedirect(request.GET.get('next') or "/"))
    else:
        raise APIForbiddenException('Logout unsuccessful, incorrect CSRF token.')
    # Gets here if successful but not HTML.
    return (metadata, data)
