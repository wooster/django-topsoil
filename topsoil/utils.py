from django.http import HttpResponse

class HttpResponseException(Exception):
    """Used to wrap an `HttpResponse` and raise it so it doesn't get
       intermingled with data emitted by an `Emitter` object's render
       method. The wrapped response is available in the `response`
       member variable."""
    def __init__(self, response):
        self.response = response

class HttpResponseNotImplemented(HttpResponse):
    def __init__(self):
        super(HttpResponseNotImplemented, self).__init__(content='Not Implemented', content_type='text/plain', status=501)
