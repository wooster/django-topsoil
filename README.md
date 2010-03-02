Note: Pre-release software. This is a work in progress and is not ready for
public consumption.

topsoil
=======
topsoil is a mini-framework for writing web APIs on top of your Django applications.

topsoil borrows heavily from django-piston.

On REST
-------
The framework makes no attempt at being RESTful. A big difference is that
in topsoil a resource may have a different endpoint for editing the resource.
So, if I have a place model, the URL structure might look like:
<pre>
/places/1
/places/1/edit
/places/1/delete
</pre>

If the resource is to be returned as json, the URLs might look like:
<pre>
/places/1.json
/places/1/edit.json
/places/1/delete.json
</pre>

Whereas with a fully RESTful API, you'd want:
<pre>
/places/1
</pre>

With GET, PUT, POST, and DELETE being used to differentiate actions upon
that resource and HTTP accept headers being used to determine the output
type.

While you can certainly do this with topsoil, it's not the default. I think
the default topsoil behavior more closely fits the model most web applications
use in practice.

Further, topsoil takes the approach that you might want to have something
like:
<pre>
/places/1.html
/places/1.fragment?last_id=2
</pre>

Where ".fragment" is used to indicate JSON output being loaded into the HTML
page dynamically. To do this, we'd simply add a new "fragment" output type
that exports JSON. Ditto for:
<pre>
/places/1.vcf
/places/1.kml
/places/1.rss
/places/1.atom
</pre>

Which was where I found myself when I decided to write this framework. These
output formats are part of a de facto web API. topsoil makes it easier to
make them de jure.
