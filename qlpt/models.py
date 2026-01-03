from django.db import models

class PhuongTien(models.Model):
    don_vi_quan_ly = models.CharField(max_length=255)
    loai_phuong_tien = models.CharField(max_length=255)
    nhan_hieu = models.CharField(max_length=255)
    nhan_hieu_sat_xi = models.CharField(max_length=255)
    bien_kiem_soat = models.CharField(max_length=255)
    nguyen_nhan_hu_hong = models.TextField()
    bien_phap_thuc_hien = models.TextField(blank=True, null=True)
    ket_qua = models.CharField(max_length=255,blank=True, null=True)
    nguoi_quan_ly = models.CharField(max_length=255, blank=True, null=True)
    de_xuat = models.TextField(blank=True, null=True)
    du_tru_kinh_phi = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.bien_kiem_soat