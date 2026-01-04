from rest_framework import serializers
from ..models import PhuongTienHuHong

class PhuongTienHuHongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhuongTienHuHong
        fields = '__all__'


from qlpt.models import Chung_loai, Danh_muc_kho, Danh_muc_nguon_cap, Chi_tiet_phieu_nhap, Phieu_nhap
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
        fields = ('id','ten','chung_loai','files')

class Chi_tiet_phieu_nhap_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Chi_tiet_phieu_nhap
        fields = "__all__"
class Phieu_nhap_Serializer(serializers.ModelSerializer):
    phuong_tiens = Chi_tiet_phieu_nhap_Serializer(many=True,required=False)
    class Meta:
        model = Phieu_nhap
        # fields = '__all__'
        fields = ("id","thoi_gian","quyetdinh","note","success","kho_xuat","kho_nhap","nguon_cap","phuong_tiens")

    def create(self, validated_data):
        # 1. Lấy dữ liệu chi tiết ra, mặc định là danh sách trống nếu không có
        chitiets_data = validated_data.pop('phuong_tiens', [])
        
        if not chitiets_data:
            raise serializers.ValidationError({"phuong_tiens": "Không có dữ liệu xuất/nhập"})

        # 2. Tạo Phieu_nhap trước để có ID (Primary Key)
        phieu_nhap = Phieu_nhap.objects.create(**validated_data)

        # 3. Tạo các chi tiết liên quan
        try:
            for chitiet in chitiets_data:
                # Đảm bảo không bị chồng chéo dữ liệu phieu_nhap nếu có trong chitiet
                chitiet.pop('phieu_nhap', None)
                Chi_tiet_phieu_nhap.objects.create(phieu_nhap=phieu_nhap, **chitiet)
        except Exception as e:
            phieu_nhap.delete()
            raise serializers.ValidationError({"error": f"Lỗi khi tạo chi tiết: {str(e)}"})

        # 4. QUAN TRỌNG: Trả về đối tượng đã có đầy đủ ID
        return phieu_nhap

    def update(self, instance, validated_data):
        nested_data = validated_data.pop('phuong_tiens')
        instance = super().update(instance,validated_data)
        instance.phuong_tiens.clear()
        for data in nested_data:
            instance.phuong_tiens.create(**data)
        return instance

class Danh_muc_kho_Serializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Danh_muc_kho
        fields = "__all__"
    def get_children(self,obj):
        serializer = Danh_muc_kho_Serializer(instance=obj.children,many=True)
        return serializer.data

class Danh_muc_nguon_cap_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Danh_muc_nguon_cap
        fields = "__all__"

class Chung_loaiSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Chung_loai
        fields = ("id","ten","maso","children")
    def get_children(self,obj):
        serializer = Chung_loaiSerializer(instance=obj.children,many=True)
        return serializer.data