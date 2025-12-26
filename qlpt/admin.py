from django.contrib import admin
from .models import PhuongTien

@admin.register(PhuongTien)
class PhuongTienAdmin(admin.ModelAdmin):
    list_display = ('don_vi_quan_ly', 'loai_phuong_tien', 'nhan_hieu', 'nhan_hieu_sat_xi', 'bien_kiem_soat', 'nguyen_nhan_hu_hong', 'bien_phap_thuc_hien', 'ket_qua')