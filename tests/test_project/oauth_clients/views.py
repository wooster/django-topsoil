from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from forms import OAuthApplicationForm
from models import OAuthApplication

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

@login_required
def oauth_authorize(request, token, callback, params):
    """View in which a user authorizes an OAuth consumer application.
       Set this view in settings.py with the OAUTH_AUTHORIZE_VIEW
       setting, like so:
       OAUTH_AUTHORIZE_VIEW = 'oauth_clients.views.oauth_authorize' """
    return HttpResponse('Callback view.#!!')
