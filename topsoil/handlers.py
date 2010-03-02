from emitters import EmitterFactory
from utils import HttpResponseException, HttpResponseNotImplemented

class BaseHandler(object):
    handler_map = {'GET':'read', 'POST':'create', 'PUT':'update', 'DELETE':'delete'}
    allowed_methods = ('read', 'create', 'update', 'delete')
    format = 'html'
    default_format = 'html'
    
    _handler_method = None
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.format = self.determine_format(*args, **kwargs)
        
    def get_handler_method(self):
        """Reutrns the function which handles the request. The default
           behavior of this method is to uppercase the request method of
           the given request, map that to the name of a function in the
           handler variable handler_map, then return a tuple containing
           the name of the function and the function object
           corresponding to that function name."""
        if not self._handler_method:
            request_method = self.request.method.upper()
            if request_method == "PUT":
                #!! fix Django bug
                pass
            f_name = self.handler_map.get(request_method)
            self._handler_method = (f_name, getattr(self, f_name, None))
        return self._handler_method
        
    def determine_format(self, *args, **kwargs):
        format = kwargs.get('emitter_format', None)
        if not format:
            format = self.request.GET.get('format', self.default_format)
        return format
    
    def read(self, *args, **kwargs):
        raise HttpResponseException(HttpResponseNotImplemented())
    
    def create(self, *args, **kwargs):
        raise HttpResponseException(HttpResponseNotImplemented())
    
    def update(self, *args, **kwargs):
        raise HttpResponseException(HttpResponseNotImplemented())
    
    def delete(self, *args, **kwargs):
        raise HttpResponseException(HttpResponseNotImplemented())

