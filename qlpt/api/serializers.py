from rest_framework import serializers
from ..models import PhuongTienHuHong
from django.db import transaction

from qlpt import models
from django.db.models import Sum

class PhuongTienHuHongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhuongTienHuHong
        fields = "__all__"


from qlpt.models import (
    Chung_loai,
    Danh_muc_kho,
    Danh_muc_nguon_cap,
    Chi_tiet_phieu_nhap,
    Phieu_nhap,
)
from qlpt.models import Tai_lieu_phuong_tien, File
from rest_framework import serializers


class File_Serializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class Tai_lieu_phuong_tien_Serializer(serializers.ModelSerializer):
    files = File_Serializer(many=True)

    class Meta:
        model = Tai_lieu_phuong_tien
        fields = ("id", "ten", "chung_loai", "files")

class Chi_tiet_kemtheo_Serializer(serializers.ModelSerializer):
    """Serializer tối giản để tránh load lại các FK không cần thiết"""
    class Meta:
        model = Chi_tiet_phieu_nhap
        # Chỉ liệt kê những gì cần hiển thị ở bảng kèm theo
        fields = ['id', 'chung_loai', 'ten', 'so_luong',]
class Chi_tiet_phieu_nhap_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Chi_tiet_phieu_nhap
        fields = ['id', 'chung_loai', 'ten', 'so_luong','nguon_cap','nguyen_gia','nam_cap']
        # fields = "__all__"

    def get_fields(self):
        # Gọi phương thức cha để lấy các field mặc định
        fields = super().get_fields()
        # Thêm field đệ quy vào đây
        fields["kemtheo"] = Chi_tiet_kemtheo_Serializer(
            many=True,
            required=False,
        )
        return fields


class Phieu_nhap_Serializer(serializers.ModelSerializer):
    phuong_tiens = Chi_tiet_phieu_nhap_Serializer(many=True, required=False)

    class Meta:
        model = Phieu_nhap
        fields = (
            "id",
            "thoi_gian",
            "quyetdinh",
            "note",
            "success",
            "kho_xuat",
            "kho_nhap",
            "nguon_cap",
            "phuong_tiens",
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']:
            # Trả về cực ít dữ liệu để kết thúc request ngay lập tức
            return {
                'id': instance.id,
                'success': True,
                'message': 'Cập nhật thành công và đã tối ưu hóa dữ liệu trả về.'
            }
        representation = super().to_representation(instance)
        # LẤY TỪ CACHE: prefetch_related đã đưa hết phuong_tiens vào memory
        all_phuong_tiens = instance.phuong_tiens.all()
        # LỌC BẰNG PYTHON: Không dùng .filter() của database
        root_items = [item for item in all_phuong_tiens if item.parent_item_id is None]
        # Gán lại dữ liệu
        representation["phuong_tiens"] = Chi_tiet_phieu_nhap_Serializer(
            root_items, many=True, context=self.context
        ).data

        return representation
    def validate(self, data):
        kho_xuat = data.get('kho_xuat')
        phuong_tiens = data.get('phuong_tiens', [])

        if kho_xuat:
            for pt in phuong_tiens:
                # Chỉ chạy query kiểm tra nếu là kho xuất
                cl = pt.get('chung_loai')
                ten = pt.get('ten')
                sl_dang_xuat = pt.get('so_luong')

                # Tính tồn kho (Tối ưu: gom các query này lại nếu có thể)
                stats = Chi_tiet_phieu_nhap.objects.filter(
                    chung_loai=cl, ten=ten, phieu_nhap__success=True
                ).aggregate(
                    tong_nhap=Sum('so_luong', filter=models.Q(phieu_nhap__kho_nhap=kho_xuat)),
                    tong_xuat=Sum('so_luong', filter=models.Q(phieu_nhap__kho_xuat=kho_xuat))
                )
                
                ton_kho = (stats['tong_nhap'] or 0) - (stats['tong_xuat'] or 0)
                if sl_dang_xuat > ton_kho:
                    raise serializers.ValidationError(f"Sản phẩm {ten} không đủ tồn kho (Còn: {ton_kho})")
        return data

    def create(self, validated_data):
        chitiets_data = validated_data.pop("phuong_tiens", [])
        if not chitiets_data:
            raise serializers.ValidationError(
                {"phuong_tiens": "Không có dữ liệu xuất/nhập"}
            )

        # Sử dụng atomic để bảo vệ tính toàn vẹn dữ liệu
        with transaction.atomic():
            phieu_nhap = Phieu_nhap.objects.create(**validated_data)

            for chitiet in chitiets_data:
                # 1. Tách dữ liệu kèm theo của từng phương tiện
                # Lưu ý: Thay "kemtheo" bằng đúng tên field ở Serializer con nếu cần
                kemtheo_data = chitiet.pop("kemtheo", [])
                chitiet.pop("phieu_nhap", None)

                # 2. Tạo phương tiện chính
                phuongtien_chinh = Chi_tiet_phieu_nhap.objects.create(
                    phieu_nhap=phieu_nhap, **chitiet
                )

                # 3. Tạo phương tiện kèm theo (con)
                for kemtheo in kemtheo_data:
                    kemtheo.pop("phieu_nhap", None)
                    kemtheo.pop("parent_item", None)
                    Chi_tiet_phieu_nhap.objects.create(
                        parent_item=phuongtien_chinh,
                        phieu_nhap=phieu_nhap,  # Gán cùng phiếu nhập để dễ quản lý
                        **kemtheo
                    )

        return phieu_nhap

    def update(self, instance, validated_data):
        phuong_tiens_data = validated_data.pop("phuong_tiens", None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if phuong_tiens_data is not None:
                # Xóa nhanh
                instance.phuong_tiens.all().delete()

                pt_chinh_objs = []
                kt_raw_data = []

                for chitiet in phuong_tiens_data:
                    kemtheo_list = chitiet.pop("kemtheo", [])
                    
                    # Chuyển object thành ID để bulk_create nhanh hơn
                    clean_data = {}
                    for key, value in chitiet.items():
                        if key in ['phieu_nhap', 'parent_item']: continue
                        # Nếu value là object model, lấy .id
                        clean_data[f"{key}_id" if hasattr(value, 'id') else key] = value.id if hasattr(value, 'id') else value

                    pt_chinh_objs.append(Chi_tiet_phieu_nhap(phieu_nhap=instance, **clean_data))
                    kt_raw_data.append(kemtheo_list)

                # Bulk Create root items
                created_pts = Chi_tiet_phieu_nhap.objects.bulk_create(pt_chinh_objs)

                # Bulk Create children
                kt_objs = []
                for i, pt_chinh in enumerate(created_pts):
                    for kt in kt_raw_data[i]:
                        clean_kt = {}
                        for k, v in kt.items():
                            if k in ['phieu_nhap', 'parent_item', 'kemtheo']: continue
                            clean_kt[f"{k}_id" if hasattr(v, 'id') else k] = v.id if hasattr(v, 'id') else v
                        
                        kt_objs.append(Chi_tiet_phieu_nhap(
                            parent_item=pt_chinh, 
                            phieu_nhap=instance, 
                            **clean_kt
                        ))
                
                if kt_objs:
                    Chi_tiet_phieu_nhap.objects.bulk_create(kt_objs)

        return instance


class Danh_muc_kho_Serializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Danh_muc_kho
        fields = "__all__"

    def get_children(self, obj):
        serializer = Danh_muc_kho_Serializer(instance=obj.children, many=True)
        return serializer.data


class Danh_muc_nguon_cap_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Danh_muc_nguon_cap
        fields = "__all__"


class Chung_loaiSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chung_loai
        fields = ("id", "ten", "maso", "children")

    def get_children(self, obj):
        serializer = Chung_loaiSerializer(instance=obj.children, many=True)
        return serializer.data
