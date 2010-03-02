from django.http import HttpResponse
from exceptions import APIForbiddenException

FORMAT_PATTERN = "(\.(?P<emitter_format>\w+))?"

class HttpResponseNotImplemented(HttpResponse):
    def __init__(self):
        super(HttpResponseNotImplemented, self).__init__(content='Not Implemented', content_type='text/plain', status=501)

DEFAULT_API_PREFIX = '/api'
DEFAULT_API_FORMATS = ('json', 'xml',)
DEFAULT_NONAPI_FORMATS = ('html',)

def default_formatter(request, *args, **kwargs):
    is_api = request.path.lower().startswith(DEFAULT_API_PREFIX)
    format = kwargs.get('emitter_format', None)
    if not format:
        if is_api:
            default = DEFAULT_API_FORMATS[0]
        else:
            default = DEFAULT_NONAPI_FORMATS[0]
        format = request.GET.get('format', default)
    if is_api:
        if format not in DEFAULT_API_FORMATS:
            raise APIForbiddenException(message="Format forbidden here: %s" % format)
    elif format not in DEFAULT_NONAPI_FORMATS:
        raise APIForbiddenException(message="Format forbidden here: %s" % format)
    return format
