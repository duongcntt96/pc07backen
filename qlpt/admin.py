from django.contrib import admin
from .models import PhuongTienHuHong

@admin.register(PhuongTienHuHong)
class PhuongTienAdmin(admin.ModelAdmin):
    list_display = ('don_vi_quan_ly', 'loai_phuong_tien', 'nhan_hieu', 'nhan_hieu_sat_xi', 'bien_kiem_soat', 'nguyen_nhan_hu_hong', 'bien_phap_thuc_hien', 'ket_qua')

from .models import Chung_loai, Danh_muc_kho, Danh_muc_nguon_cap, Phieu_nhap, Chi_tiet_phieu_nhap
from .models import Tai_lieu_phuong_tien, File

admin.site.register(Danh_muc_kho)
admin.site.register(Danh_muc_nguon_cap)
admin.site.register(Chung_loai)
admin.site.register(Phieu_nhap)
admin.site.register(Chi_tiet_phieu_nhap)

admin.site.register(Tai_lieu_phuong_tien)
admin.site.register(File)