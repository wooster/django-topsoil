from django.db import models
from django.utils.translation import ugettext as _
from oauth_provider.consts import CONSUMER_STATES, MAX_URL_LENGTH
from oauth_provider.models import Consumer

class OAuthApplication(models.Model):
    CLIENT = 1
    BROWSER = 2
    APPLICATION_TYPES = ((CLIENT, _('Client')), (BROWSER, _('Browser')))
    
    consumer = models.ForeignKey(Consumer)
    
    application_url = models.URLField(verify_exists=False)
    organization_name = models.CharField(max_length=255, unique=True)
    organization_url = models.URLField(verify_exists=False)
    
    application_type = models.SmallIntegerField(choices=APPLICATION_TYPES)
    callback_url = models.CharField(max_length=MAX_URL_LENGTH, blank=True)
    
    read_permission = models.BooleanField(default=True)
    write_permission = models.BooleanField(default=True)
    delete_permission = models.BooleanField(default=False)
    login_permission = models.BooleanField(default=False)
    
    user_count = models.IntegerField(default=0)
    
    def get_absolute_url(self):
        return "/oauth_clients/%d" % self.id

    def approval_status(self):
        status = self.consumer.status
        for state, readable in CONSUMER_STATES:
            if status == state:
                return readable
        return _('Unknown')
    
    def permissions_readable(self):
        perms = []
        if self.read_permission:
            perms.append('read')
        if self.write_permission:
            perms.append('write')
        if self.delete_permission:
            perms.append('delete')
        if self.login_permission:
            perms.append('login')
        return '/'.join(perms)
