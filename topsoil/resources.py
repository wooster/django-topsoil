from authenticators import NoAuthenticationAuthenticator
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.views.decorators.vary import vary_on_headers
from emitters import EmitterFactory, HttpResponseException

class BaseResource(object):
    def __init__(self, handler_factory, authenticator=None):
        self.handler_factory = handler_factory
        if not authenticator:
            self.authenticator = NoAuthenticationAuthenticator()
        else:
            self.authenticator = authenticator
        #!! Evil, evil hack to let us use the cache_page decorator on
        # resources. Should come up with a cleaner solution for caching.
        self.__name__ = self.__class__.__name__
    
    @vary_on_headers('Authorization')
    def __call__(self, request, *args, **kwargs):
        try:
            handler = self.handler_factory(request, *args, **kwargs)
            (method_name, method) = handler.get_handler_method()
            (emitter_klass, emitter_mime) = EmitterFactory.get(handler.format)

            (authenticated, challenge) = self.authenticator.authenticate(request)

            if not authenticated and callable(challenge):
                return challenge()

            if not method_name in handler.allowed_methods:
                # Theoretically we would want to send a 405 here instead.
                # However, in this model, we don't have that information
                # unless we use the default implementation to retrieve the
                # handler  method.
                return HttpResponseForbidden()
            if not method:
                raise Http404
            
            # Make sure we don't violate the function interface.
            kwargs.pop('emitter_format', None)
            (metadata, data) = method(*args, **kwargs)
            emitter = emitter_klass(request, metadata, data)
            response = HttpResponse(emitter.render(), mimetype=emitter_mime)
            return response
        except HttpResponseException, e:
            print "got exception:", e #!!
            return e.response
        except ValueError, e:
            raise
        except TypeError, e:
            raise
        except Http404, e:
            raise
        except Exception, e:
            #!! Need error handling strategy.
            raise
