from django.http import HttpResponse
from django.shortcuts import render

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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
        args['category_slug'] = category.slug
    except Category.DoesNotExist:
        pass
    return render(request, 'rango/category.html', args)

def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()
    context_dict = {'form':form, 'category': cat, 'category_slug': category_name_slug}
    return render(request, 'rango/add_page.html', context_dict)
