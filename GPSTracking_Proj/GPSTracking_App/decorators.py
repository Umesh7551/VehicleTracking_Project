from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def allowed_user(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("You are not authorized user to access this page. Thank You!!!")
        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all[0].name

        if group == 'fleetowner':
            return redirect('fleetowner_page')
        if group == 'fleetowner_support_personnel':
            return redirect('fleetowner_support_personnel_page')
        if group == 'ed_admin_support_personnel':
            return redirect('ed_admin_support_personnel_page')
        if group == 'ed_admin':
            return view_func(request, *args, **kwargs)

    return wrapper_function
