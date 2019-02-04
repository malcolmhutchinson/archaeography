"""The authority module holds functions which do two things.

    Some of them return True or False, and are used to answer the
    question "is the user allowed to do this?". These functions accept
    a user object and can be used in view decorators.

    The other kind of function compiles lists of (link, text) tuples,
    providing the tools the user is permitted. These functions accept
    a request object, and will determine tools depending on what
    resource is currently being accessed.

"""

import nzaa.models


def applications(request):
    """Build the list of apps the user can see.

    Unauthenticated users do not get any apps. The list of
    authenticated users depends on what groups they are a member of.

    Items on this list should appear in alphabetical order, with exceptions.

    """

    if not request.user.is_authenticated():
        return None

    apps = [('/member/' + request.user.username, 'your homepage')]
    if request.user.groups.filter(name='nzaa'):
        apps.append(('/nzaa/', 'nzaa site records'))

    return apps


def group_memberships(request):
    """Return a list of the groups this user is a member of."""

    if not request.user.is_authenticated():
        return None

    groups = []
    for group in request.user.groups.all():
        groups.append(group)

    return groups

def your_stuff(request):
    """List of navigation commands peculiar to the user."""

    if not request.user.is_authenticated():
        return None

    stuff = [('/member/' + request.user.username, 'your homepage'),]
    
    if request.user.groups.filter(name='nzaa'):
        if nzaa.models.Update.objects.filter(
                owner=request.user.username).exists():
            stuff.append(
                ('/nzaa/updates/' + request.user.username, 'your site updates')
            )
        if nzaa.models.NewSite.objects.filter(
                owner=request.user.username).exists():
            stuff.append(
                ('/nzaa/newsites/' + request.user.username, 'your new sites')
            )
        if nzaa.models.SiteList.objects.filter(
                owner=request.user.username).exists():
            stuff.append(
                ('/nzaa/sitelists/' + request.user.username, 'your site lists')
            )

    if request.user.groups.filter(name='boundary'):
        stuff.append(
            ('/nzaa/boundaries/', 'your boundary reports')
        )
    
    return stuff

