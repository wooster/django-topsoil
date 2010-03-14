from client.place_client import OAuthClient
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import PlaceForm
from oauth import oauth

@login_required
def places_all(request):
    profile = request.user.get_profile()
    token = oauth.OAuthToken.from_string(profile.access_token)
    client = OAuthClient(settings.PLACES_CONSUMER_KEY, settings.PLACES_CONSUMER_SECRET, access_token=token)
    places = client.all_places()
    context = {'places':places['places'], 'title':places['title']}
    return render_to_response('places/list.html', context_instance=RequestContext(request, context))

@login_required
def places_add(request):
    profile = request.user.get_profile()
    token = oauth.OAuthToken.from_string(profile.access_token)
    client = OAuthClient(settings.PLACES_CONSUMER_KEY, settings.PLACES_CONSUMER_SECRET, access_token=token)
    request_method = request.method.upper()
    context = {}
    if request_method == 'GET':
        context['form'] = PlaceForm()
    elif request_method == 'POST':
        form = PlaceForm(request.POST)
        context['form'] = form
        if form.is_valid():
            result = client.add_place(name=form.cleaned_data['name'], url=form.cleaned_data['url'])
            if result.get('place', False):
                return HttpResponseRedirect('/places')
            else:
                context['error'] = 'Unable to save place.'
    return render_to_response('places/add.html', context_instance=RequestContext(request, context))
