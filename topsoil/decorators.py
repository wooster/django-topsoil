from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.cache import cache
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils.cache import get_cache_key, learn_cache_key
from django.views.decorators.vary import vary_on_headers
from authenticators import NoAuthenticationAuthenticator
from emitters import EmitterFactory
from exceptions import APILoginRequiredException, HttpResponseException
from functools import update_wrapper, wraps
from utils import default_formatter, default_is_request_api

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

"""
Basically, here we are going to want to have a function that we can
use to alternatively:
- require login on a non-API request
- require OAuth access for a resource on an API request

@oauth_required
@login_required
@login_or_oauth_required
@oauth_read_required
@oauth_write_required

"""

def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL
    
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect()

def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
