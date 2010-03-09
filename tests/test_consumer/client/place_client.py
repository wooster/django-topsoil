from django.conf import settings
from django.utils import simplejson
from oauth import oauth
import sys
import time

# HTTP Stuff
import httplib
import socket
import urllib
import urllib2

PLACES_SERVER = getattr(settings, 'PLACES_SERVER', 'http://127.0.0.1:8081')
REQUEST_TOKEN_URL = '%s/oauth/request_token/' % PLACES_SERVER
USER_AUTHORIZATION_URL = '%s/oauth/authorize/' % PLACES_SERVER
ACCESS_TOKEN_URL = '%s/oauth/access_token/' % PLACES_SERVER
SIGNIN_URL = '%s/oauth/authenticate/' % PLACES_SERVER # Twitter style login.

class PlacesBasicAuthOpener(object):
    use_auth = False
    auth_header = 'Authorization'
    def __init__(self, username=None, password=None):
        """urllib2 has really braindead authentication handling. So, we
           roll our own."""
        if username and password:
            self.use_auth = True
            raw = "%s:%s" % (username, password)
            self.auth = 'Basic %s' % base64.b64encode(raw).strip()
    def urlopen(self, request, timeout=10):
        if self.use_auth:
            request.add_header(self.auth_header, self.auth)
        # I used to use socket to set the timeout, but that interferes
        # with the multiprocessing package. Basically, don't ever use
        # a python version less than 2.5. You shouldn't anyway.
        return urllib2.urlopen(request, timeout=timeout)

class NotFoundError(Exception):
    """Used to bubble up 404 errors."""
    def __init__(self, urlerror):
        self.urlerror = urlerror

class PlacesClient(object):
    RATE_LIMIT_RETRIES = 5
    def __init__(self, username=None, password=None):
        self.opener = PlacesBasicAuthOpener(username, password)
        self.user_agent = 'Topsoil/0.1'
    
    def build_request(self, url, post_data=None):
        request = None
        if post_data is not None:
            data = urllib.urlencode(post_data)
            request = urllib2.Request(url, data)
        else:
            request = urllib2.Request(url)
        if self.user_agent:
            request.add_header('User-Agent', self.user_agent)
        return request
            
    def retrieve_url(self, url, raise_notfound=False, post_data=None, request=None):
        if request is None:
            request = self.build_request(url, post_data=post_data)
        try:
            response = None
            # Retry on hitting a rate limit.
            for i in xrange(0, self.RATE_LIMIT_RETRIES):
                try:
                    response = self.opener.urlopen(request)
                    if response.code != 200:
                        continue
                    break
                except urllib2.HTTPError, e:
                    if e.code == 404 and raise_notfound:
                        raise NotFoundError(e)
                    elif e.code != 400:
                        raise e
                    # Twitter-style rate limiting.
                    reset = e.hdrs.get("X-RateLimit-Reset", 0)
                    if reset == 0:
                        raise e
                    delay = int(reset) - time.time()
                    time.sleep(delay + 1)
            if response is None:
                return None
            contents = response.read()
            return contents
        except (urllib2.URLError, socket.error, httplib.BadStatusLine), e:
            # I kid you not, you need to handle these.
            #!!print >> sys.stderr, "HTTP Error:", e
            return None
        except Exception, e:    
            #!!print >> sys.stderr, "Unknown Exception:", e
            raise e
            return None
    
    def retrieve_json(self, url, raise_notfound=False, post_data=None):
        """Same as above, but tries to return JSON."""
        contents = self.retrieve_url(url, raise_notfound=raise_notfound, post_data=post_data)
        try:
            json = simplejson.loads(contents)
        except ValueError, e:
            return None
        if type(json) == dict and json.has_key('error'):
            return None
        return json
    
    def all_places(self):
        url = '%s/api/places.json' % PLACES_SERVER
        return self.retrieve_json(url)
    
    def get_place(self, place_id):
        url = '%s/api/places/%d.json' % place_id
        return self.retrieve_json(url)
    
    def add_place(self, name='', url=''):
        url = '%s/api/places/add.json' % PLACES_SERVER
        post_data = {'name':name, 'url':url}
        return self.retrieve_json(url, post_data=post_data)
    
    def edit_place(self, name='', url=''):
        url = '%s/api/places/%d/edit.json' % PLACES_SERVER
        post_data = {'name':name, 'url':url}
        return self.retrieve_json(url, post_data=post_data)

class OAuthOpener(PlacesBasicAuthOpener):
    def __init__(self):
        pass
    def urlopen(self, request, timeout=10):
        return (super, OAuthOpener, self).urlopen(request, timeout=timeout)


class OAuthClient(PlacesClient):
    def __init__(self, consumer_key, consumer_secret, access_token=None):
        super(OAuthClient, self).__init__(self)
        self.access_token = access_token
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
    
    def build_request(self, url, post_data=None, token=None):
        if not token:
            token = self.access_token
        method = 'POST'
        if post_data is None and token is None:
            method = 'GET'
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=url, parameters=post_data, http_method=method)
        self.sign_request(oauth_request)
        if post_data is None:
            oauth_post_data = None
            oauth_url = oauth_request.to_url()
        else:
            oauth_post_data = oauth_request.to_postdata()
            oauth_url = oauth_request.get_normalized_http_url()
        request = super(OAuthClient, self).build_request(oauth_url)
        if oauth_post_data:
            request.add_data(oauth_post_data)
        return request
    
    def retrieve_url(self, url, raise_notfound=False, post_data=None, request=None):
        if request is None:
            request = self.build_request(url, post_data=post_data)
        return super(OAuthClient, self).retrieve_url(url, raise_notfound=raise_notfound, post_data=post_data, request=request)
        
    def sign_request(self, request, signature_method=oauth.OAuthSignatureMethod_HMAC_SHA1()):
        request.sign_request(signature_method, self.consumer, self.access_token)
        
    def request_token(self, url=REQUEST_TOKEN_URL):
        token = None
        response = self.retrieve_url(url)
        if response:
            token = oauth.OAuthToken.from_string(response)
        return token
    
    def access_token(self, url=ACCESS_TOKEN_URL):
        return self.request_token(url=url)
    
    def authorization_url(self, token, url=USER_AUTHORIZATION_URL):
        request = self.build_request(url, token=token)
        return request.get_full_url()
    
    def signin_url(self, token, url=SIGNIN_URL):
        return self.authorization_url(token, url)
    
    def verify_credentials(self):
        url = '%s/api/accounts/verify_credentials.json'
        data = self.retrieve_json(url)
        return data.get('user', None)
