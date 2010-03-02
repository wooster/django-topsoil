import django.db.models.options as dboptions
from django.conf import settings
dboptions.DEFAULT_NAMES = dboptions.DEFAULT_NAMES + ('topsoil_exclude', )

