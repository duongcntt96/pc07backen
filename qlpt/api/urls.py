from django.urls import path, include
from .views import PhuongTienViewSet



from rest_framework.routers import DefaultRouter
from .views import Chung_loai_viewSet, Danh_muc_kho_viewSet, Danh_muc_nguon_cap_viewSet, Chi_tiet_phieu_nhap_ViewSet, Phieu_nhap_ViewSet, Tai_lieu_phuong_tien_viewSet
from .views import Thuc_luc, Ton_kho, Text_to_speak

router = DefaultRouter()

# router.register('phuongtien', PhuongTienViewSet)
router.register('chungloai', Chung_loai_viewSet)
router.register('kho', Danh_muc_kho_viewSet)
router.register('nguoncap', Danh_muc_nguon_cap_viewSet)
router.register('phieunhap', Phieu_nhap_ViewSet)
router.register('chitietphieunhap', Chi_tiet_phieu_nhap_ViewSet)
router.register('tailieuphuongtien', Tai_lieu_phuong_tien_viewSet)

urlpatterns = [
    path('/', include(router.urls)),
    path('/thucluc', Thuc_luc.as_view()),
    path('/tonkho', Ton_kho.as_view()),
    # path('/texttospeak', Text_to_speak.as_view())
]