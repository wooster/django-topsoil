from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.translation import ugettext as _
from oauth.oauth import OAuthError
from oauth_provider.decorators import CheckOAuth
from oauth_provider.utils import initialize_server_request, send_oauth_error
from utils import default_is_request_api

class ApiCsrfExemptionMiddleware(object):
    """If a request is an API request, this will attempt to exempt it
       from CSRF protection.
       This should only be used with corresponding middleware to disable
       cookie-based authentication on API requests.
       """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if getattr(view_func, 'csrf_exempt', False):
            return None
        if getattr(request, 'csrf_processing_done', False):
            return None
        if default_is_request_api(request):
            request.csrf_processing_done = True
        return None
    
    def process_response(self, request, response):
        if getattr(response, 'csrf_processing_done', False):
            return response
        elif default_is_request_api(request):
            response.csrf_processing_done = True
        return response

class ApiOauthMiddleware(object):
    """Middleware which attempts to use OAuth authentication on API 
       requests and cookie-based authentication on normal requests."""
    auth_middleware = None
    def __init__(self):
        self.auth_middleware = AuthenticationMiddleware()
    
    def process_request(self, request):
        if not default_is_request_api(request):
            return self.auth_middleware.process_request(request)
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if default_is_request_api(request):
            resource_name = getattr(request, 'oauth_resource_name', None)
            if CheckOAuth.is_valid_request(request):
                try:
                    consumer, token, parameters = CheckOAuth.validate_token(request)
                except OAuthError, e:
                    return send_oauth_error(e)
                if resource_name and token.resource.name != resource_name:
                    return send_oauth_error(OAuthError(_('You are not allowed to access this resource.')))
                elif consumer and token:
                    return None
            return send_oauth_error(OAuthError(_('Invalid request parameters.')))
        return None
