from django.http import HttpResponse
from django.shortcuts import render

from rango.models import Category, Page

def index(request):
    args = {}
    category_list = Category.objects.order_by('-likes')[:5]
    mostViewedPages = Page.objects.order_by('-views')[:5]
    
    args['mostViewedPages'] = mostViewedPages
    args['categories'] = category_list
    return render(request, 'rango/index.html', args)

def about(request):
    return render(request, 'rango/about.html')

def category(request, category_name_slug):
    args = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        args['category_name'] = category.name

        pages = Page.objects.filter(category=category)


        args['pages'] = pages
        args['category'] = category

    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', args)
