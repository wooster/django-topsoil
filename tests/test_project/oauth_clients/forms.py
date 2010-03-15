from django import forms
from django.utils.translation import ugettext as _
from models import OAuthApplication
from oauth_provider.consts import OUT_OF_BAND
from oauth_provider.models import Consumer

class RevokeApplicationForm(forms.Form):
    application_id = forms.IntegerField(widget=forms.HiddenInput)

class OAuthApplicationForm(forms.Form):
    READ_ONLY = 1
    READ_AND_WRITE = 2
    READ_WRITE_AND_DELETE = 3
    ACCESS_TYPE_CHOICES = (
        (READ_WRITE_AND_DELETE, _('Read, Write, & Delete')), 
        (READ_AND_WRITE, _('Read & Write')), 
        (READ_ONLY, _('Read Only')))
    
    application_name = forms.CharField(max_length=255, label=_('Application Name'))
    application_description = forms.CharField(widget=forms.Textarea, label=_('Description'))
    application_url = forms.URLField(label=_('Application Website'))
    organization_name = forms.CharField(max_length=255, label=_('Organization'))
    organization_url = forms.URLField(label=_('Website'))
    application_type = forms.ChoiceField(widget=forms.RadioSelect, choices=OAuthApplication.APPLICATION_TYPES, label=_('Application Type'))
    callback_url = forms.URLField(label=_('Callback URL'), required=False)
    access_type = forms.ChoiceField(widget=forms.RadioSelect, choices=ACCESS_TYPE_CHOICES, label=_('Default Access type'))
    use_for_login = forms.BooleanField(widget=forms.CheckboxInput, label=_('Use for login'))
    
    def save(self, user, application=None):
        if self.errors:
            raise ValueError
        p = self.cleaned_data
        consumer = None
        if application is None:
            application = OAuthApplication()
            consumer = Consumer.objects.create_consumer(p['application_name'], user=user)
            application.consumer = consumer
        else:
            consumer = application.consumer
            consumer.name = p['application_name']
        consumer.description = p['application_description']
        consumer.save()
        application.application_url = p['application_url']
        application.organization_name = p['organization_name']
        application.organization_url = p['organization_url']
        application.application_type = p['application_type']
        if application.application_type == OAuthApplication.CLIENT:
            application.callback_url = OUT_OF_BAND
        else:
            application.callback_url = p['callback_url']
        access_type = p.get('access_type', OAuthApplicationForm.READ_ONLY)
        if access_type == OAuthApplicationForm.READ_WRITE_AND_DELETE:
            application.read_permission = True
            application.write_permission = True
            application.delete_permission = True
        elif access_type == OAuthApplicationForm.READ_AND_WRITE:
            application.read_permission = True
            application.write_permission = True
        else:
            application.read_permission = True
        application.login_permission = p['use_for_login']
        application.save()
        return application
