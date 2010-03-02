from django.core.cache import cache
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils.cache import get_cache_key, learn_cache_key
from django.views.decorators.vary import vary_on_headers
from authenticators import NoAuthenticationAuthenticator
from emitters import EmitterFactory
from exceptions import APILoginRequiredException, HttpResponseException
from functools import update_wrapper, wraps
from utils import default_formatter

def resource(authenticator=NoAuthenticationAuthenticator, formatter=default_formatter):
    """The guts of topsoil. Wrap your view methods in this, then return
       tuples of (metadata, data) in order to make resources."""
    def decorator(view_func):
        @vary_on_headers('Authorization')
        def inner(request, *args, **kwargs):
            try:
                format = formatter(request, *args, **kwargs)
                (emitter_klass, emitter_mime) = EmitterFactory.get(format)
    
                # Make sure we don't violate the function interface.
                kwargs.pop('emitter_format', None)
                kwargs['format'] = format
                (metadata, data) = view_func(request, *args, **kwargs)
                emitter = emitter_klass(request, metadata, data)
                response = HttpResponse(emitter.render(), mimetype=emitter_mime)
                return response
            except APILoginRequiredException, e:
                auth = authenticator().challenge_response()
                return auth
            except HttpResponseException, e:
                return e.response
            except (ValueError, TypeError, Http404, Exception), e:
                #!! Need error handling strategy.
                #!! Send email on error, etc.
                raise
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(inner)
    return decorator
