from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from forms import OAuthApplicationForm
from models import OAuthApplication
from oauth.oauth import OAuthError
from oauth_provider.utils import initialize_server_request, send_oauth_error
from oauth_provider.views import user_authorization

@login_required
def oauth_applications(request):
    """Show all OAuth applications registered by the authenticated user."""
    applications = OAuthApplication.objects.filter(consumer__user=request.user)
    context = {'title':'Applications'}
    context['applications'] = applications
    return render_to_response('oauth_client_list.html', context_instance=RequestContext(request, context))

@login_required
def oauth_application_details(request, application_id):
    """Show the details of an OAuth applications registered by the logged
       in user."""
    application = get_object_or_404(OAuthApplication, id=application_id, consumer__user=request.user)
    context = {'title':'Application - %s' % application.consumer.name}
    context['application'] = application
    return render_to_response('oauth_client_details.html', context_instance=RequestContext(request, context))
    
@login_required
def oauth_application_add(request):
    """Register a new OAuth application."""
    context = {'title':'Add Application'}
    if request.POST:
        form = OAuthApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(request.user)
            return HttpResponseRedirect(application.get_absolute_url())
    else:
        form = OAuthApplicationForm()
    context['form'] = form
    return render_to_response('oauth_client_register.html', context_instance=RequestContext(request, context))

@login_required
def oauth_application_edit(request, application_id):
    """Edit an OAuth application."""
    application = get_object_or_404(OAuthApplication, id=application_id, consumer__user=request.user)
    context = {'title':'Edit Application - %s' % application.consumer.name}
    if request.POST:
        form = OAuthApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(request.user, application=application)
            return HttpResponseRedirect(application.get_absolute_url())
    else:
        initial = {
            'application_name':application.consumer.name,
            'application_description':application.consumer.description,
            'application_url':application.application_url,
            'organization_name':application.organization_name,
            'organization_url':application.organization_url,
            'application_type':application.application_type,
            'callback_url':application.callback_url
        }
        t = OAuthApplicationForm.READ_ONLY
        if application.delete_permission:
            t = OAuthApplicationForm.READ_WRITE_AND_DELETE
        elif application.write_permission:
            t = OAuthApplicationForm.READ_AND_WRITE
        initial['access_type'] = t
        initial['use_for_login'] = application.login_permission
        
        form = OAuthApplicationForm(initial=initial)
    context['form'] = form
    return render_to_response('oauth_client_edit.html', context_instance=RequestContext(request, context))

@login_required
def oauth_application_reset_key(request, application_id):
    """Resets the application's consumer key and secret."""
    application = get_object_or_404(OAuthApplication, id=application_id, user=request.user)
    if request.POST:
        application.consumer.generate_random_codes()
    return HttpResponseRedirect(application.get_absolute_url())

#@login_required
def oauth_authorize(request, token, callback, params):
    """View in which a user authorizes an OAuth consumer application.
       Set this view in settings.py with the OAUTH_AUTHORIZE_VIEW
       setting, like so:
       OAUTH_AUTHORIZE_VIEW = 'oauth_clients.views.oauth_authorize' """
    context = {'token':token, 'callback':callback, 'params':params}
    application = get_object_or_404(OAuthApplication, consumer=token.consumer)
    context['application'] = application
    return render_to_response('oauth_authorize.html', context_instance=RequestContext(request, context))


@login_required
def oauth_authorize_wrapper(request):
    """Wraps the actual oauth user_authorization view, providing for a 
       mechanism for the user to cancel the request."""
    if request.POST:
        if request.POST.get('cancel', False):
            oauth_server, oauth_request = initialize_server_request(request)
            try:
                token = oauth_server.fetch_request_token(oauth_request)
            except OAuthError, err:
                return send_oauth_error(err)
            application = get_object_or_404(OAuthApplication, consumer=token.consumer)
            context = {'oauth_token':token.key, 'application':application}
            return render_to_response('oauth_authorize_denied.html', context_instance=RequestContext(request, context))
    return user_authorization(request)

@login_required
def oauth_authenticate(request, token, callback, params):
    "http://twitter.com/oauth/authenticate?oauth_nonce=90366957&oauth_timestamp=1268517793&oauth_consumer_key=OtbyqgXwg8Xvcx6jWamA&oauth_signature_method=HMAC-SHA1&oauth_version=1.0&oauth_token=tEJA3uyAkiNO8PZA0yOnJ3LZGzc5gcgjHkc7Y11Nk&oauth_signature=qhjKRJYRuSlVnj1xW4opbWC67BY%3D"
    "http://127.0.0.1:8081/oauth/authenticate/?oauth_nonce=53622166&oauth_timestamp=1268345627&oauth_consumer_key=x2aV8unHhXj8paGa&oauth_signature_method=HMAC-SHA1&oauth_version=1.0&oauth_token=8maV3UKPtZd62VF2&oauth_signature=U4jNhKybUT%2BUN7pNOfDwHJ6%2BdEc%3D"
    #!! application = get_object_or_404(OAuthApplication, )
    context = {}
    context['user'] = request.user
    context['oauth_token'] = token.key
    return HttpResponse('Authenticate view is unimplemented!!')
