# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

def test_index(request, template_name="index.html"):
    return render_to_response(template_name, {'title':'Topsoil Test App'}, context_instance=RequestContext(request))
