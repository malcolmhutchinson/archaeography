"""Member views

These include things a mamber does by oneself. Archaeological reports
for boundary files to start with.

"""
from django.shortcuts import render

import home
import nzaa
from nzaa.authorise import nzaa_member


@login_required
def boundaries(request):
    """View and upload a member's boundary files."""

    template = ''
    context = build_context(request)

    return render(request, template, context)


@login_required
def home(request, command=None):
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


# ANCILLARY FUNCTIONS

def build_context(request):
    """Return a dictionary containing site infrastructure structures.

    Start with the home context variable, which contains site-wide
    infrastructure, and add what is common to the archlib application.

    """

    context = home.views.build_context(request)
    context['nav'] = 'nzaa/member.html'
    context['stylesheet'] = 'css/nzaa.css'
    context['notifications'] = []
    context['loginform'] = None
    context['filekeeper'] = authority.filekeeper(request.user)
    context['member'] = nzaa_member(request.user)
    context['buttons'] = None
    context['URL'] = settings.BASE_URL

    if nzaa_member:
        context['authorised'] = True

    return context

    





