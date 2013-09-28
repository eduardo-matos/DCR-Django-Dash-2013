from django.http import HttpResponse
from django.shortcuts import render_to_response
from py_w3c.validators.html.validator import HTMLValidator
from recursive_validator.validator import Validator 

def home(request):
    return render_to_response("core/index.html")

def errors(request, url):
    vld = HTMLValidator()

    vld.validate(url)
    return render_to_response("core/lista-erro.html", {'errors': vld.errors})
