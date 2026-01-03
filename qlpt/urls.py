from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PhuongTienViewSet

router = SimpleRouter()
router.register(r'phuongtien', PhuongTienViewSet)

urlpatterns = [
    path('', include(router.urls)),
]