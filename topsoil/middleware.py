from utils import default_is_request_api

class ApiCsrfExemptionMiddleware(object):
    """If a request is an API request, this will attempt to exempt it
       from CSRF protection.
       This should only be used with corresponding middleware to disable
       cookie-based authentication on API requests.
       """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(callback, 'csrf_exempt', False):
            return None
        if getattr(request, 'csrf_processing_done', False):
            return None
        if default_is_request_api(request):
            request.csrf_processing_done = True
        return None
    
    def process_response(self, request, response):
        if getattr(response, 'csrf_processing_done', False):
            return response
        elif default_is_request_api(request):
            response.csrf_processing_done = True
        return response
