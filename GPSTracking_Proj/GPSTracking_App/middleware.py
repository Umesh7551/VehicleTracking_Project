from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedRedirectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in [reverse('ed_admin_support_dashboard'), reverse('fleetowner_dashboard'), reverse('fleetowner_support_dashboard')]:
            if request.user.is_authenticated:
                # if request.user.groups.filter(name='ed_admin').exists():
                #     return redirect(reverse('ed_admin_dashboard'))
                if request.user.groups.filter(name='ed_admin_support_person').exists():
                    return redirect(reverse('ed_admin_support_dashboard'))
                elif request.user.groups.filter(name='fleetowner').exists():
                    return redirect(reverse('fleetowner_dashboard'))
                elif request.user.groups.filter(name='fleetowner_support_person').exists():
                    return redirect(reverse('fleetowner_support_dashboard'))

        response = self.get_response(request)
        return response
