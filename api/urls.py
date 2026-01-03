
from django.urls import path, include
# from rest_framework import routers

# from . import views

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('user', include('user.api.urls')),
    path('qlpt/', include('qlpt.urls')),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]