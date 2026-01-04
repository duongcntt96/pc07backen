from django.urls import path, include

urlpatterns = [
    path('user', include('user.api.urls')),
    path('qlpt', include('qlpt.api.urls')),
]