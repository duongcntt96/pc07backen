from rest_framework import serializers
from ..models import PhuongTienHuHong
from django.db import transaction


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


class Chi_tiet_phieu_nhap_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Chi_tiet_phieu_nhap
        fields = "__all__"

    def get_fields(self):
        # Gọi phương thức cha để lấy các field mặc định
        fields = super().get_fields()
        # Thêm field đệ quy vào đây
        fields["kemtheo"] = Chi_tiet_phieu_nhap_Serializer(
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
        """
        Ghi đè hiển thị: Chỉ đưa các phương tiện GỐC (không có cha) vào mảng phuong_tiens.
        Các phương tiện kèm theo sẽ tự động chui vào trong mục 'kemtheo' của phương tiện gốc
        nhờ vào Serializer đệ quy.
        """
        # 1. Lấy dữ liệu mặc định (đang bị lặp)
        representation = super().to_representation(instance)

        # 2. Lọc lại queryset: Chỉ lấy những chi tiết có parent_item là NULL
        root_phuong_tiens = instance.phuong_tiens.filter(parent_item__isnull=True)

        # 3. Gán lại dữ liệu đã lọc vào key 'phuong_tiens'
        representation["phuong_tiens"] = Chi_tiet_phieu_nhap_Serializer(
            root_phuong_tiens, many=True
        ).data

        return representation

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
            # Cập nhật các trường thông tin chung của Phiếu nhập
            instance = super().update(instance, validated_data)

            if phuong_tiens_data is not None:
                # Xóa dữ liệu cũ
                instance.phuong_tiens.all().delete()

                # Tạo mới lại y hệt logic hàm create
                for chitiet in phuong_tiens_data:
                    kemtheo_data = chitiet.pop("kemtheo", [])
                    chitiet.pop("phieu_nhap", None)

                    pt_chinh = Chi_tiet_phieu_nhap.objects.create(
                        phieu_nhap=instance, **chitiet
                    )

                    for kt in kemtheo_data:
                        kt.pop("phieu_nhap", None)
                        kt.pop("parent_item", None)
                        kt.pop("kemtheo", None)
                        Chi_tiet_phieu_nhap.objects.create(
                            parent_item=pt_chinh, phieu_nhap=instance, **kt
                        )

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
