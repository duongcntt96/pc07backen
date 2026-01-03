from rest_framework import permissions

from user.models import thong_tin_ca_nhan, bo_phan


class ObjectPermission(permissions.BasePermission):
    message = "Not have permission"

    def has_permission(self, request, view):
        print(request.user.profile.all()[0].team.all())

        if (request.user.is_authenticated):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.quan_ly and request.user.profile.all():
            return obj.quan_ly in request.user.profile.all()[0].team.all()
        else:
            return False


class IsPostOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_staff


class IsAuthenticatedOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS):
            return True
        if (request.user.is_authenticated):
            return True
        return False
