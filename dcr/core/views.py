from django.http import HttpResponse

def home(request):
    from py_w3c.validators.html.validator import HTMLValidator

    vld = HTMLValidator()

    # validate
    vld.validate("http://www.comprafacil.com.br/")

    # look for warnings
    return HttpResponse(vld.errors[0]['message'])