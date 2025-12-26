from django.db import models

class PhuongTien(models.Model):
    don_vi_quan_ly = models.CharField(max_length=255)
    loai_phuong_tien = models.CharField(max_length=255)
    nhan_hieu = models.CharField(max_length=255)
    nhan_hieu_sat_xi = models.CharField(max_length=255)
    bien_kiem_soat = models.CharField(max_length=255)
    nguyen_nhan_hu_hong = models.TextField()
    bien_phap_thuc_hien = models.TextField()
    ket_qua = models.CharField(max_length=255)

    def __str__(self):
        return self.bien_kiem_soat