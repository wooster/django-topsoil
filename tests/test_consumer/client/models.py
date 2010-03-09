from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class PlacesUser(models.Model):
    username = models.CharField(max_length=64, unique=True)
    has_used_oauth = models.BooleanField(default=False, db_index=True)

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    places_user = models.ForeignKey(PlacesUser, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True, editable=False)
    
    def __str__(self):
        return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
