from django.http import HttpResponse
from django.shortcuts import render_to_response
from py_w3c.validators.html.validator import HTMLValidator

def home(request):
    vld = HTMLValidator()
    vld.validate("http://icrach.com")
# valid = urllib.urlopen('http://validator.w3.org/check?uri=http://icrach.com').info().getheader('x-w3c-validator-status') == 'Valid'
    return render_to_response("core/index.html", {'errors': vld.errors})