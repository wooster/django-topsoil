from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models
from django.forms import BaseForm
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader, RequestContext
from django.utils import simplejson, feedgenerator
from django.utils.encoding import smart_unicode, StrAndUnicode
from django.utils.functional import Promise
from django.utils.xmlutils import SimplerXMLGenerator
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from exceptions import HttpResponseException

LOWERCASE_MODEL_NAMES = True
POINT_TYPE_NAME_X = 'longitude'
POINT_TYPE_NAME_Y = 'latitude'
TOPSOIL_EXCLUSIONS = {
    User:['password', 'email', 'is_superuser', 'is_staff', 'last_login']
    }
TOPSOIL_DEFAULT_DETAIL_LEVEL = 2

class NamedDict(object):
    """Used by the default `Emitter` to represent a dictionary with a name."""
    def __init__(self, name, dictionary=None):
        if dictionary is None:
            dictionary = {}
        self.name = name
        self.dictionary = dictionary
    def dict(self):
        return self.dictionary

class EmitterFactory(object):
    """Keeps track of which emitters should be used for which
       output formats."""
    EMITTERS = {}
    
    @classmethod
    def register(cls, format, klass, mime_type):
        cls.EMITTERS[format] = (klass, mime_type)
    
    @classmethod
    def get(cls, format):
        if cls.EMITTERS.has_key(format):
            return cls.EMITTERS.get(format)
        raise ValueError("No emitter found for format %s." % format)

class Emitter(object):
    metadata = {}
    data = {}
    request = None
    _cachedFieldsForModel = {}
    _detailLevel = TOPSOIL_DEFAULT_DETAIL_LEVEL
    _currentDetailLevel = 1
    
    def __init__(self, request, metadata, data):
        self.request = request
        self.metadata = metadata
        self.data = data
        # 0 for infinite, 1 for no recurse on model, 2 and above
        # to show detail for that level of models.
        self.detailLevel = metadata.get('detail', 0)
    
    def fieldsForModel(self, model_klass):
        if self._cachedFieldsForModel.has_key(model_klass):
            return self._cachedFieldsForModel[model_klass]
        fields = []
        exclusions = getattr(model_klass._meta, 'topsoil_exclude', [])
        if TOPSOIL_EXCLUSIONS.has_key(model_klass):
            exclusions.extend(TOPSOIL_EXCLUSIONS[model_klass])
        for field in model_klass._meta.fields:
            if field.attname not in exclusions and field.name not in exclusions:
                fields.append(field)
        self._cachedFieldsForModel[model_klass] = fields
        return fields
    
    def construct(self):
        """May raise `HttpResponseException`."""
        def _any(data):
            ret = None
            if isinstance(data, list):
                ret = _list(data)
            elif isinstance(data, dict):
                ret = _dict(data)
            elif isinstance(data, Decimal):
                ret = str(data)
            elif hasattr(data, 'topsoil_encode') and callable(getattr(data, 'topsoil_encode')):
                ret = _any(data.topsoil_encode())
            elif isinstance(data, models.query.QuerySet):
                ret = _list(data)
            elif isinstance(data, models.Model):
                ret = _model(data)
            elif isinstance(data, BaseForm):
                ret = _form(data)
            elif isinstance(data, Point):
                ret = _any({POINT_TYPE_NAME_X:data.get_x(), POINT_TYPE_NAME_Y:data.get_y()})
            elif isinstance(data, HttpResponse):
                raise HttpResponseException(data)
            elif isinstance(data, Promise):
                # Django error messages are promised values.
                ret = unicode(data)
            else:
                ret = data
            return ret
        
        def _list(data):
            return [_any(v) for v in data]
        
        def _dict(data):
            ret = {}
            for key, value in data.items():
                ret[key] = _any(value)
            return ret
        
        def _fk(data, field):
            return _any(getattr(data, field.name))
        
        def _model(data):
            model_name = data.__class__.__name__
            if LOWERCASE_MODEL_NAMES:
                model_name = model_name.lower()
            ret = {}
            fields = self.fieldsForModel(data.__class__)
            for field in fields:
                show_detail = True
                print self._currentDetailLevel, self._detailLevel
                if self._detailLevel != 0 and self._currentDetailLevel >= self._detailLevel:
                    show_detail = False
                if field.rel and show_detail:
                    # Related field.
                    self._currentDetailLevel += 1
                    ret[field.name] = _fk(data, field)
                    self._currentDetailLevel -= 1
                else:
                    ret[field.attname] = _any(getattr(data, field.attname))
            #!! Todo:
            # Many to many, relationships, and foreign keys.
            
            return NamedDict(model_name, ret)
        
        def _form(data):
            ret = {}
            inputs = []
            for name, field in data.fields.items():
                bf = MyBoundField(data, field, name)
                bf_errors = data.error_class(bf.errors)
                attrs = {'name':bf.name, 'hidden':bf.is_hidden, 'required':bf.is_required}
                if bf.data:
                    attrs['value'] = unicode(bf.data)
                input_field = {'attrs':attrs, 'errors':_any(data.error_class(bf.errors))}
                inputs.append(NamedDict('input', input_field))
            ret['inputs'] = inputs
            top_errors = data.non_field_errors()
            if top_errors:
                ret['errors'] = top_errors
            return NamedDict(None, ret)
        
        return _any(self.data)
        
    def render(self):
        raise NotImplementedError("render not implemented in emitter.")

class HTMLEmitter(Emitter):
    """Expects a template value in the metadata which names the template
       to render with the data as the context."""
    def construct(self):
        return self.data
    def render(self):
        template = self.metadata.get('template', None)
        if template is None:
            return HttpResponseServerError()
        return loader.render_to_string(template, context_instance=RequestContext(self.request, self.data))

EmitterFactory.register('html', HTMLEmitter, 'text/html; charset=utf-8')
EmitterFactory.register('xhtml', HTMLEmitter, 'application/xhtml+xml; charset=utf-8')

class TopsoilJSONEncoder(DateTimeAwareJSONEncoder):
    """A JSON encoder which understands `NamedDict` objects."""
    def default(self, o):
        if isinstance(o, NamedDict):
            return o.dict()
        else:
            return super(TopsoilJSONEncoder, self).default(o)

class JSONEmitter(Emitter):
    def render(self):
        callback = self.request.GET.get('callback')
        serialized = simplejson.dumps(self.construct(), cls=TopsoilJSONEncoder, ensure_ascii=False, indent=4)
        if callback:
            return "%s(%s)" % (callback, serialized)
        else:
            return serialized

EmitterFactory.register('json', JSONEmitter, 'application/json; charset=utf-8')

class XMLEmitter(Emitter):
    def _xml(self, xml, data, resource_name='resource'):
        if isinstance(data, (list, tuple)):
            for item in data:
                #!! maybe array?
                self._xml(xml, item)
        elif isinstance(data, dict):  
            if resource_name:
                xml.startElement(resource_name, {})
            for key, value in data.iteritems():
                xml.startElement(str(key), {})
                self._xml(xml, value, resource_name=None)
                xml.endElement(str(key))
            if resource_name:
                xml.endElement(resource_name)
        elif isinstance(data, NamedDict):
            self._xml(xml, data.dict(), resource_name=data.name)
        else:
            xml.characters(smart_unicode(data))
    
    def render(self):
        stream = StringIO.StringIO()
        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement('response', {'version':getattr(settings, 'API_VERSION', '1.0')})
        xml.startElement('request', {'path':self.request.path})
        xml.endElement('request')
        self._xml(xml, self.construct(), resource_name=None)
        xml.endElement('response')
        xml.endDocument()
        return stream.getvalue()

EmitterFactory.register('xml', XMLEmitter, 'application/xml; charset=utf-8')

# class AtomEmitter(Emitter):
#     """Expect:
#        In data: `title`, `link` (defaults to request path), 
#        `description`, `items`, `item_titles`.
#        In metadata: `item_template` (template for each item in `items`)."""
#     def render(self):
#         title = self.data.get('title', '')
#         print dir(self.request)
#         link = self.data.get('link', self.request.build_absolute_uri())
#         description = self.data.get('description', '')
#         feed = feedgenerator.Atom1Feed(title=title, link=link, description=description)
#         for item in self.data.get('items', []):
#             pass #!!!!
#         return feed.writeString("UTF-8")
#     
# EmitterFactory.register('atom', AtomEmitter, 'application/atom+xml')

class MyBoundField(StrAndUnicode):
    "Mirror of functionality in django.forms.forms.BoundField"
    def __init__(self, form, field, name):
        self.form = form
        self.field = field
        self.name = name
        self.html_name = form.add_prefix(name)

    def _errors(self):
        """
        Returns an ErrorList for this field. Returns an empty ErrorList
        if there are none.
        """
        return self.form.errors.get(self.name, self.form.error_class())
    errors = property(_errors)

    def _is_hidden(self):
        "Returns True if this BoundField's widget is hidden."
        return self.field.widget.is_hidden
    is_hidden = property(_is_hidden)
    
    def _is_required(self):
        "Returns True if this BoundField's value is required."
        return self.field.required
    is_required = property(_is_required)

    def _data(self):
        """
        Returns the data for this BoundField, or None if it wasn't given.
        """
        return self.field.widget.value_from_datadict(self.form.data, self.form.files, self.html_name) or self.form.initial.get(self.name, self.field.initial)
    data = property(_data)
