from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class bo_phan(models.Model):
    ten = models.CharField(max_length=100)
    slogan = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.ten

    class Meta:
        verbose_name = 'Bộ phận'
        verbose_name_plural = 'Bộ phận'
        ordering = ['id']

class chuc_vu(models.Model):
    ten = models.CharField(max_length=100)
    order = models.IntegerField(null=True,blank=True)
    def __str__(self):
        return self.ten

    class Meta:
        verbose_name = 'Chức vụ'
        verbose_name_plural = 'Chức vụ'
        ordering = ['id']

class cap_bac(models.Model):
    ten = models.CharField(max_length=100)
    def __str__(self):
        return self.ten
    class Meta:
        verbose_name = 'Cấp bậc'
        verbose_name_plural = 'Cấp bậc'
        ordering = ['id']

class thong_tin_ca_nhan(models.Model):
    username = models.ForeignKey(
        User,related_name="profile", on_delete=models.CASCADE, null=True, blank=True)
    avatar = models.ImageField(
        upload_to='static/images/upload/', null=True, blank=True)
    ten = models.CharField(verbose_name="Họ và tên", max_length=100)
    team = models.ForeignKey(bo_phan,on_delete=models.CASCADE, verbose_name="Bộ phận", related_name="userset" ,blank=True, null=True)
    cap_bac = models.ForeignKey(cap_bac, verbose_name="Cấp bậc", on_delete=models.CASCADE, blank=True, null=True)
    chuc_vu = models.ForeignKey(chuc_vu, verbose_name="chức vụ", on_delete=models.CASCADE, null=True, blank=True)
    ngay_sinh = models.DateField(verbose_name="Ngày sinh", blank=True, null=True)
    que_quan = models.CharField(max_length=500,verbose_name="Quê quán", blank=True, null=True)
    ho_khau = models.CharField(max_length=500,verbose_name="Hộ khẩu", blank=True, null=True)
    sdt = models.CharField(max_length=10,verbose_name="Số điện thoại", blank=True, null=True)
    trinh_do_chinh_tri = models.CharField(max_length=50,verbose_name="Trình độ chính trị", blank=True, null=True)
    trinh_do_chuyen_mon = models.CharField(max_length=50, verbose_name="Trình độ chuyên môn", blank=True, null=True)
    ngay_vao_nganh = models.DateField(verbose_name="Ngày vào ngành", blank=True, null=True)
    nam_nhan_cong_tac = models.PositiveIntegerField(verbose_name='Năm nhận công tác', validators=[
        MinValueValidator(1980), MaxValueValidator(2024)], null=True, blank=True)
    nam_nghi_cong_tac = models.PositiveIntegerField(verbose_name='Năm nghỉ/chuyển công tác/xuất ngũ', validators=[
        MinValueValidator(2000), MaxValueValidator(3000)], null=True, blank=True)

    active = models.BooleanField(verbose_name="Active", blank=True, null=True, default=True)
    ghi_chu = models.CharField(max_length=500,verbose_name="Thông tin bổ sung", null=True, blank=True)

    # def active(self):
    #     if self.username:
    #         return self.username.is_active
    #     else:
    #         return False
    def __str__(self):
        # self.cap_bac=None
        # self.save()
        return self.ten

    class Meta:
        verbose_name = 'Thông tin cán bộ, chiến sĩ'
        verbose_name_plural = 'Thông tin cán bộ, chiến sĩ'
        ordering = ['chuc_vu','cap_bac','ngay_sinh']

