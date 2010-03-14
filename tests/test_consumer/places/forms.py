from django import forms

class PlaceForm(forms.Form):
    name = forms.CharField(max_length=128)
    url = forms.URLField(max_length=256)
