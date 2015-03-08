from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime
import json
import urllib, urllib2

from rango.bing_search import run_query

def index(request):
    args = {}
    category_list = Category.objects.order_by('-likes')[:5]
    mostViewedPages = Page.objects.order_by('-views')[:5]
    args['mostViewedPages'] = mostViewedPages
    args['categories'] = category_list

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 60:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    args['visits'] = visits

    return render(request,'rango/index.html', args)

def about(request):
    args = {}
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 60:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    args['visits'] = visits

    return render(request, 'rango/about.html', args)

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_slug'] = category_name_slug
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

@login_required
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

@login_required
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
                request.method = "GET"
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()
    context_dict = {'form':form, 'category': cat, 'category_slug': category_name_slug}
    return render(request, 'rango/add_page.html', context_dict)

def passwordChangeDone(request):
    return render(request, 'registration/passwordchange_complete.html')

def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def register_profile(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        profile_form = UserProfileForm(request.POST)
        if profile_form.is_valid():
            try:
                userprofile = UserProfile.objects.get(user=user)
                userprofile.website = request.POST['website']
                userprofile.picture = request.FILES['picture']
                userprofile.save()
            except ObjectDoesNotExist as e:
                userprofile = None
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.picture = request.FILES['picture']
                profile.save()
        return index(request)
    else:
        form = UserProfileForm(request.GET)
        return render(request, 'rango/profile_registration.html', {'profile_form': form})

@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    args = {}
    try:
        userprofile = UserProfile.objects.get(user=user)
    except ObjectDoesNotExist as e:
        print e
        userprofile = None
    args['user'] = user
    args['userprofile'] = userprofile
    return render(request, 'rango/profile.html', args)
