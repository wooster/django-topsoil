from django.conf import settings

# Fix stupid bug in Django trunk.
if 'django.core.context_processors.request' not in settings.TEMPLATE_CONTEXT_PROCESSORS:
    settings.TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.request',)
