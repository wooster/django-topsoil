from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField(max_length=256, verify_exists=False)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta(object):
        topsoil_exclude = ['date']
    
    def get_absolute_url(self):
        return "/places/%i" % self.id
    
    def get_edit_url(self):
        return "/places/%i/edit" % self.id
