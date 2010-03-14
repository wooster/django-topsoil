from django.conf import settings
from django.contrib.auth.models import User
from models import PlacesUser, UserProfile
from place_client import OAuthClient

CONSUMER_KEY = getattr(settings, 'PLACES_CONSUMER_KEY')
CONSUMER_SECRET = getattr(settings, 'PLACES_CONSUMER_SECRET')

class PlacesBackend:
    """Based on: http://www.djangosnippets.org/snippets/1473/"""
    def authenticate(self, access_token):
        places = OAuthClient(CONSUMER_KEY, CONSUMER_SECRET, access_token)
        try:
            userinfo = places.verify_credentials()
        except Exception, e:
            return None
        
        try:
            places_user = PlacesUser.objects.get(id=userinfo['id'])
        except PlacesUser.DoesNotExist:
            places_user = PlacesUser(id=userinfo['id'])
            places_user.username = userinfo['username']
        if places_user is None:
            return None
        places_user.has_used_oauth = True
        places_user.save()
        
        username = userinfo['username']
        user, created = User.objects.get_or_create(username=username)
        if created:
            # Set a random password so user cannot log in using
            # built-in auth.
            tmp_password = User.objects.make_random_password(length=12)
            user.set_password(tmp_password)
        user.save()
        
        # Get user profile.
        try:
            userprofile = user.get_profile()
        except UserProfile.DoesNotExist:
            userprofile = UserProfile.objects.get_or_create(user=user)
        userprofile.places_user = places_user
        userprofile.access_token = str(access_token)
        userprofile.save()
        return user
        
    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except:
            return None
