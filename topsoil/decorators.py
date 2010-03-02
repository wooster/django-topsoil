from django.core.cache import cache
from django.utils.cache import get_cache_key, learn_cache_key
from functools import wraps

def soil(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        raise NotImplementedException
    return wraps(view_func)(_wrapped_view_func)
