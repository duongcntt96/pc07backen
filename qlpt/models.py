from django.db import models
from django.db.models import Sum
from django.core.validators import MaxValueValidator, MinValueValidator


class PhuongTienHuHong(models.Model):
    don_vi_quan_ly = models.CharField(max_length=255)
    loai_phuong_tien = models.CharField(max_length=255)
    nhan_hieu = models.CharField(max_length=255)
    nhan_hieu_sat_xi = models.CharField(max_length=255)
    bien_kiem_soat = models.CharField(max_length=255)
    nguyen_nhan_hu_hong = models.TextField()
    bien_phap_thuc_hien = models.TextField(blank=True, null=True)
    ket_qua = models.CharField(max_length=255, blank=True, null=True)
    nguoi_quan_ly = models.CharField(max_length=255, blank=True, null=True)
    de_xuat = models.TextField(blank=True, null=True)
    du_tru_kinh_phi = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return self.bien_kiem_soat


class Chung_loai(models.Model):
    ten = models.CharField(verbose_name="Tên", max_length=500, null=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="Nhóm chủng loại",
        related_name="children",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    maso = models.CharField(
        verbose_name="Mã số (Để trống để tự động tạo mã số)",
        max_length=10,
        null=True,
        blank=True,
    )
    create_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.maso == None:
            length = len(self.parent.children.all())
            if length > 8:
                __maso = str(length + 1)
            else:
                __maso = "0" + str(length + 1)
            # Khởi tạo mã số phương tiện theo mã nhóm phương tiện
            self.maso = self.parent.maso + __maso
        self.ten = self.ten.strip()
        super(Chung_loai, self).save(*args, **kwargs)

    class Meta:
        ordering = ["maso"]
        verbose_name = "Chủng loại"
        verbose_name_plural = "Chủng loại"

    def __str__(self):
        if self.maso != None:
            return str(self.maso) + " - " + self.ten
        return self.ten


class Danh_muc_kho(models.Model):
    ten = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        related_name="children",
        verbose_name="Đơn vị quản lý cấp trên",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    active = models.BooleanField(default=True)
    # Vị trí kho: vĩ độ và kinh độ (nullable)
    latitude = models.DecimalField(
        verbose_name="Vĩ độ", max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        verbose_name="Kinh độ", max_digits=9, decimal_places=6, null=True, blank=True
    )
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Danh mục kho"
        verbose_name_plural = "Danh mục kho"
        ordering = ["id"]

    def __str__(self):
        return self.ten


class Danh_muc_nguon_cap(models.Model):
    ten = models.CharField(max_length=200)
    mo_ta = models.CharField(max_length=500, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Danh mục nguồn cấp"
        verbose_name_plural = "Danh mục nguồn cấp"

    def __str__(self):
        return self.ten


class Phieu_nhap(models.Model):
    thoi_gian = models.DateField(verbose_name="Thời gian nhập")
    kho_xuat = models.ForeignKey(
        Danh_muc_kho,
        verbose_name="Kho xuất",
        related_name="export_data",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    kho_nhap = models.ForeignKey(
        Danh_muc_kho,
        verbose_name="Kho nhập",
        related_name="import_data",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    nguon_cap = models.ForeignKey(
        Danh_muc_nguon_cap,
        verbose_name="Nguồn cấp",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    quyetdinh = models.CharField(max_length=200, null=True, blank=True)
    note = models.CharField(max_length=500, null=True, blank=True)
    success = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     super(Phieu_nhap, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Phiếu nhập"
        verbose_name_plural = "Phiếu nhập"
        ordering = ["-thoi_gian"]

    def __str__(self):
        return "Phiếu số " + self.pk.__str__()


class Chi_tiet_phieu_nhap(models.Model):
    phieu_nhap = models.ForeignKey(
        Phieu_nhap, related_name="phuong_tiens", on_delete=models.CASCADE, null=True,
    )
    chung_loai = models.ForeignKey(
        Chung_loai, verbose_name="Chủng loại", on_delete=models.RESTRICT,
    )
    parent_item = models.ForeignKey(
        "self",
        verbose_name="Kèm theo phương tiện",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="kemtheo",
    )

    ten = models.CharField(verbose_name="Tên", max_length=500)
    so_luong = models.BigIntegerField(verbose_name="Số lượng")
    nguyen_gia = models.PositiveBigIntegerField(
        verbose_name="Nguyên giá (VNĐ)", null=True, blank=True
    )
    nam_cap = models.PositiveIntegerField(
        verbose_name="Năm cấp",
        validators=[MinValueValidator(1900), MaxValueValidator(2025)],
        null=True,
        blank=True,
    )
    nguon_cap = models.ForeignKey(
        Danh_muc_nguon_cap,
        verbose_name="Nguồn cấp",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    hinh_anh = models.FileField(
        verbose_name="Hình ảnh", upload_to="static", null=True, blank=True
    )
    file = models.FileField(
        verbose_name="File liên quan", upload_to="static", null=True, blank=True
    )

    class Meta:
        verbose_name = "Chi tiết phiếu nhập"
        verbose_name_plural = "Chi tiết phiếu nhập"

    def __str__(self):
        return self.ten

    # def save(self, *args, **kwargs):
    #     if self.phieu_nhap.kho_xuat:
    #         nhap = Chi_tiet_phieu_nhap.objects.filter(
    #             phieu_nhap__kho_nhap=self.phieu_nhap.kho_xuat,
    #             chung_loai=self.chung_loai,
    #             ten=self.ten,
    #         ).aggregate(totals=Sum("so_luong"))
    #         xuat = Chi_tiet_phieu_nhap.objects.filter(
    #             phieu_nhap__kho_xuat=self.phieu_nhap.kho_xuat,
    #             chung_loai=self.chung_loai,
    #             ten=self.ten,
    #         ).aggregate(totals=Sum("so_luong"))
    #         if self.so_luong > ((nhap["totals"] or 0) - (xuat["totals"] or 0)):
    #             raise Exception("Không đủ hàng tồn kho để xuất")
    #         else:
    #             super(Chi_tiet_phieu_nhap, self).save(*args, **kwargs)
    #     else:
    #         super(Chi_tiet_phieu_nhap, self).save(*args, **kwargs)


class Tai_lieu_phuong_tien(models.Model):
    chung_loai = models.ForeignKey(
        Chung_loai, verbose_name="Chủng loại", on_delete=models.RESTRICT
    )
    ten = models.CharField(verbose_name="Tên phương tiện", max_length=200)


class File(models.Model):
    Tai_lieu_phuong_tien = models.ForeignKey(
        Tai_lieu_phuong_tien, related_name="files", on_delete=models.PROTECT
    )
    file = models.FileField(verbose_name="File tài liệu", upload_to="static")
