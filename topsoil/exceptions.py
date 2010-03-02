class HttpResponseException(Exception):
    """Used to wrap an `HttpResponse` and raise it so it doesn't get
       intermingled with data emitted by an `Emitter` object's render
       method. The wrapped response is available in the `response`
       member variable."""
    def __init__(self, response):
        self.response = response

class APIException(Exception):
    status_code = 400
    message = 'API Error'
    
    def __init__(self, message=None):
        if message is not None:
            self.message = message
    
    @property
    def response(self):
        response = HttpResponse(message)
        response.status_code = self.__class__.status_code
        return response

class APILoginRequiredException(APIException):
    status_code = 401
    message = 'Unauthorized'

class APIForbiddenException(APIException):
    status_code = 403
    message = 'Forbidden'
