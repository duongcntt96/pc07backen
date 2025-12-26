from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhuongTienViewSet

router = DefaultRouter()
router.register(r'phuongtien', PhuongTienViewSet)

urlpatterns = [
    path('', include(router.urls)),
]