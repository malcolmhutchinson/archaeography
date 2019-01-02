"""Archaeography website views.

"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect

import datetime
import os

import authority
import forms
import geolib.analyse
import geolib.models
import members.forms
import nzaa.analyse
import nzaa.models
import settings
import webnote

MANUALS = os.path.join(settings.STATICFILES_DIRS[0], 'manuals')

MAIN_FORM = {
    'id': 'siteRecord',
    'action': '',
    'method': 'POST',
    'class': 'mainForm',
}


def about(request):

    context = build_context(request)
    context['h1'] = 'About archaeography.nz'
    context['subhead'] = "Experiments in computational archaeology "
    context['subhead'] += "by Malcolm Hutchinson and friends"
    context['loginform'] = None

    return render(request, 'about.html', context)


def home(request):
    """The home page.

    This shows 'nohing to see here' to any unauthenticated user. Users
    will get a notification card.

    """

    template = 'home.html'
    template = 'nothingtosee.html'

    context = build_context(request)
    context['user'] = None

    if request.user.is_authenticated():
        context['user'] = request.user

    return render(request, template, context)


def login_site(request):
    """Login as a member, then go about your business. """
    context = build_context(request)
    context['h1'] = 'Log into archaeography.nz'
    context['title'] = context['h1']
    goto = '/'

    if request.user.groups.filter(name='nzaa').exists():
        context['nzaa_member'] = True

    if request.GET:
        goto = request.GET['next']

    if request.POST and request.POST['command'] == 'login':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user:
            context['user'] = user
            login(request, user)
            return redirect(goto)

        else:
            context['message'] = 'Failed attempt there, ' + username + '.'
    else:
        context['message'] = 'Please log into the site.'

    return render(request, 'login.html', context)


def logoff(request):
    logout(request)
    return redirect('/')


def manuals(request, address=None):
    """Display the manuals. """
    context = build_context(request)
    context['h1'] = 'Manuals'
    context['title'] = context['h1'] + " | archaeography.nz"
    context['loginform'] = None
    context['stylesheet'] = 'css/manuals.css'
    docroot = MANUALS
    baseurl = '/manuals'
    try:
        page = webnote.page.Page(docroot, baseurl, address)
        context['breadcrumbs'] = page.breadcrumbs()
    except webnote.page.Page.DocumentNotFound:
        page = None
        context['h1'] = 'Page not found'

    context['page'] = page

    return render(request, 'manuals.html', context)


@login_required
def userhome(request, command=None):
    """Display updates and sitelists belonging to the authenticated user. """

    context = build_context(request)
    context['h1'] = "This is your archaeography home page, "
    context['h1'] += request.user.username
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True

    # This causes trouble if the user has no associated member record.
    context['memberForm'] = forms.MemberForm(instance=request.user.member)

    context['lists'] = nzaa.models.SiteList.objects.filter(
        owner=request.user.username)
    context['updates'] = nzaa.models.Update.objects.filter(
        owner=request.user.username)

    if request.POST:
        memberForm = forms.MemberForm(
            request.POST, instance=request.user.member
        )
        if memberForm.is_valid():
            memberForm.save()
            context['memberForm'] = memberForm

    return render(request, 'home/user.html', context)


# ---------------------------------------------------------------
# Ancilliary functions (not views).
#
def build_context(request):
    """Return a dictionary contain site infrastructure structures.

    The context variable is fed to the template. This function returns
    a dictionary whichg can be used for that puirpose, continaing all
    the elements common to the whole site. It will be expanded on by
    each app.

    """

    CONTEXT = {
        'title': 'a r c h a e o g r a p h y . n z',
        'h1': 'archaeography.nz',
        'stylesheet_screen': 'css/screen.css',
        'stylesheet_printer': 'css/print.css',
        'breadcrumbs': [],
        'site_apps': [
            ('/geolib/', 'geodata library'),
            ('/manuals/', 'manuals'),
        ],
        'nav': None,
        'commands': None,
        'loginform': forms.LoginForm,
        'notifications': [],
        'user': request.user,
    }

    if request.user.groups.filter(name='nzaa').exists():
        CONTEXT['site_apps'].append(('/nzaa/', 'nzaa site records'))

    return CONTEXT
