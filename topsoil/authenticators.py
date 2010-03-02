import base64
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from oauth.oauth import OAuthError
from oauth_provider.decorators import CheckOAuth
from oauth_provider.utils import initialize_server_request, send_oauth_error

class BaseAuthenticator(object):
    def authenticate(self, request):
        return (True, None)

class NoAuthenticationAuthenticator(BaseAuthenticator):
    pass

class HttpBasicAuthenticator(BaseAuthenticator):
    def __init__(self, auth_function=authenticate, realm='API'):
        self.auth_function = authenticate
        self.realm = realm
    def authenticate(self, request):
        auth_string = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_string:
            return (False, self.challenge_response)
        try:
            (auth_type, auth_cred) = auth_string.split(' ')
            if auth_type.lower() != 'basic':
                return (False, self.challenge_response)
            auth_cred_decoded = base64.b64decode(auth_cred.strip())
            (username, password) = auth_cred_decoded.split(':', 1)
        except (ValueError, TypeError):
            return (False, self.challenge_response)
        user = self.auth_function(username=username, password=password)
        if not user:
            user = AnonymousUser()
        request.user = user
        if user in (False, None, AnonymousUser()):
            return (False, self.challenge_response)
        else:
            return (True, None)
        
    def challenge_response(self):
        response = HttpResponse('Authorization Required', content_type='text/plain', status=401)
        response['WWW-Authenticate'] = "Basic realm=\"%s\"" % self.realm
        return response

class OAuthAuthenticator(BaseAuthenticator):
    def __init__(self, resource_name=None):
        self.resource_name = resource_name
    def is_authenticated(self, request):
        if CheckOAuth.is_valid_request(request):
            try:
                consumer, token, parameters = CheckOAuth.validate_token(request)
            except OAuthError, e:
                return (False, self.make_challenge(e))
            if self.resource_name and token.resource.name != self.resource_name:
                err = OAuthError(_('You are not allowed to access this resource.'))
                return (False, self.make_challenge(err))
            elif consumer and token:
                request.user = token.user
                return (True, None)
        err = OAuthError(_('Invalid request parameters.'))
        return (False, self.make_challenge(err))
    
    def make_challenge(self, err):
        def challenge():
            return send_oauth_error(err)
        return challenge
    
    def challenge_response(self):
        return send_oauth_error()
