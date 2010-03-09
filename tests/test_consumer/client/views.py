# Create your views here.
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from oauth import oauth
from place_client import OAuthClient

def index(request, template_name="index.html"):
    return render_to_response(template_name, {'title':'OAuth Consumer Test App'}, context_instance=RequestContext(request))

def places_signin(request):
    places = OAuthClient(settings.PLACES_CONSUMER_KEY, settings.PLACES_CONSUMER_SECRET)
    request_token = places.request_token()
    request.session['request_token'] = request_token.to_string()
    signin_url = places.signin_url(request_token)
    return HttpResponseRedirect(signin_url)

def places_signout(request):
    #!! CSRF handling.
    logout(request)
    return HttpResponseRedirect('/')

def places_return(request):
    request_token = request.session.get('request_token', None)
    # If there's no request_token for the session, that means
    # we didn't redirect the user.
    if not request_token:
        # Meh. !!
        return HttpResponse('We didn\'t redirect you to the test app...')
    token = oauth.OAuthToken.from_string(request_token)
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del request.session['request_token']
        return HttpResponse('Something is wrong! Tokens do not match...')
    places = OAuthClient(settings.PLACES_CONSUMER_KEY, settings.PLACES_CONSUMER_SECRET)
    access_token = places.access_token()
    request.session['access_token'] = access_token.to_string()
    auth_user = authenticate(access_token=access_token)
    
    if auth_user:
        login(request, auth_user)
    else:
        del request.session['access_token']
        del request.session['request_token']
        return HttpResponse('Unable to authenticate you!')
    generate_session_token(request, auth_user)
    return HttpResponseRedirect("/")
