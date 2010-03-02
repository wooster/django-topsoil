from django.http import HttpResponseForbidden, HttpResponseRedirect
from topsoil.handlers import BaseHandler
from topsoil.utils import HttpResponseException
from models import Place
from forms import PlaceForm

class APIHandler(BaseHandler):
    default_api_format = 'json'
    api_formats = ('xml', 'json',)
    nonapi_formats = ('html',)
    def determine_format(self, *args, **kwargs):
        """An example which can restrict the output formats based on whether
           the request was an API request or not."""
        path = self.request.path.lower()
        is_api = path.startswith('/api')
        
        format = kwargs.get('emitter_format', None)
        if not format:
            default = self.default_format
            if is_api:
                default = self.default_api_format
            format = self.request.GET.get('format', default)
        
        path = self.request.path.lower()
        if path.startswith('/api'):
            # If the user requests eg HTML, raise error.
            if format not in self.api_formats:
                raise HttpResponseException(HttpResponseForbidden("Format forbidden here: %s" % format))
        # If user requests eg XML on normal page, raise error.
        elif format not in self.nonapi_formats:
            raise HttpResponseException(HttpResponseForbidden("Format forbidden here: %s" % format))
        return format

class EchoHandler(APIHandler):
    allowed_methods = ('read',)
    
    def read(self):
        metadata = {}
        data = {}
        if self.format == 'html':
            metadata['template'] = 'echo/echo.html'
        if self.format in ('html',):# 'rss', 'atom'):
            data['title'] = 'Echo'
        data['msg'] = self.request.GET.get('msg', '')
        return (metadata, data)

class PlaceHandler(APIHandler):
    allowed_methods = ('list', 'add', 'edit',)
    nonapi_formats = ('html',)# 'atom', )
    method_in = None
    
    def __init__(self, request, *args, **kwargs):
        super(PlaceHandler, self).__init__(request, *args, **kwargs)
        self.method_in = kwargs.pop('method', 'list')
        #if self.format == 'atom' and self.method_in.lower() != 'list':
        #    raise HttpResponseException(HttpResponseException("Format forbidden here: %s" % self.format))
    
    def get_handler_method(self):
        f_name = self.method_in.lower()
        if f_name not in self.allowed_methods:
            return (None, None)
        else:
            return (f_name, getattr(self, f_name, None))
    
    def list(self, **kwargs):
        metadata = {}
        data = {}
        place_id = kwargs.get('place_id')
        if place_id is not None:
            return self.list_one(place_id)
        data['places'] = Place.objects.all()
        data['title'] = 'All Places'
        if self.format == 'html':
            metadata['template'] = 'places/list.html'
        return (metadata, data)
    
    def list_one(self, place_id):
        metadata = {}
        data = {}
        place = Place.objects.get(id=int(place_id))
        data['place'] = place
        if self.format == 'html':
            metadata['template'] = 'places/place.html'
            data['title'] = place.name
        return (metadata, data)
    
    def add(self, **kwargs):
        metadata = {}
        data = {}
        if self.format == 'html':
            metadata['template'] = 'places/add.html'
        request_method = self.request.method.upper()
        if request_method == 'GET':
            data['form'] = PlaceForm()
        elif request_method == 'POST':
            form = PlaceForm(self.request.POST)
            try:
                place = form.save()
                if self.format == 'html':
                    raise HttpResponseException(HttpResponseRedirect(self.request.GET.get('next_page') or place.get_absolute_url()))
                else:
                    data['place'] = place
            except ValueError:
                data['form'] = form
        return (metadata, data)
    
    def edit(self, **kwargs):
        metadata = {}
        data = {}
        place_id = kwargs.get('place_id')
        request_method = self.request.method.upper()
        place = Place.objects.get(id=int(place_id))
        if self.format == 'html':
            metadata['template'] = 'places/edit.html'
        if request_method == 'GET':
            data['form'] = PlaceForm(instance=place)
        elif request_method == 'POST':
            form = PlaceForm(self.request.POST, instance=place)
            try:
                place = form.save()
                if self.format == 'html':
                    raise HttpResponseException(HttpResponseRedirect(self.request.GET.get('next_page') or place.get_absolute_url()))
                else:
                    data['place'] = place
            except ValueError:
                data['form'] = form
        return (metadata, data)
    