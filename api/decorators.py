from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrap(self, request, *args, **kwargs):
            print(request.user)
            print(request.user.groups.all()[0].name)
            print(request.headers['User-Agent'])
            print(request.headers['Authorization'])
            if request.user.groups.all()[0].name in allowed_roles:
                return view_func(self, request, *args, **kwargs)
            else:
                return HttpResponse("No role permission")
        return wrap
    return decorator
