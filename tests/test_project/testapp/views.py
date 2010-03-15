# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

def test_index(request, template_name="index.html"):
    context = {'title':'Topsoil Test App'}
    return render_to_response(template_name, context, context_instance=RequestContext(request))


