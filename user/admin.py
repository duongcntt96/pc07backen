from django.contrib import admin

from .models import bo_phan, cap_bac, chuc_vu, thong_tin_ca_nhan

class TTCNAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = ["ten"]

admin.site.register(bo_phan)
admin.site.register(cap_bac)
admin.site.register(chuc_vu)
admin.site.register(thong_tin_ca_nhan,TTCNAdmin)