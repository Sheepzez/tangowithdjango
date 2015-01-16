from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    args = {'boldmessage': "I am bold font from the context"}
    return render(request, 'rango/index.html', args)

def about(request):
    return render(request, 'rango/about.html')
