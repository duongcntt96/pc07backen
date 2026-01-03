from rest_framework import serializers
from user.models import bo_phan, cap_bac, chuc_vu, thong_tin_ca_nhan
from django.contrib.auth.models import User, Group


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = thong_tin_ca_nhan
        fields =  [
            "id",
            "active",
            "avatar",
            "ten",
            "ngay_sinh",
            "que_quan",
            "ho_khau",
            "sdt",
            "trinh_do_chinh_tri",
            "trinh_do_chuyen_mon",
            "nam_nhan_cong_tac",
            "nam_nghi_cong_tac",
            "cap_bac",
            "chuc_vu",
            "team",
            "ghi_chu"
            ]
        

class bo_phan_Serializer(serializers.ModelSerializer):
    # member = UserProfileSerializer(source='userset', many=True, read_only=True)
    class Meta:
        model = bo_phan
        # fields = "__all__"
        fields = ['id','ten','slogan',]

class chuc_vu_Serializer(serializers.ModelSerializer):
    class Meta:
        model = chuc_vu
        fields = "__all__"

class cap_bac_Serializer(serializers.ModelSerializer):
    class Meta:
        model = cap_bac
        fields = "__all__"


###################################### 

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ['id', 'username', 'email',
        #   'date_joined', 'groups', 'team_set']
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def validate_username(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Tên đăng nhập quá ngắn')
        return value

    def validate_first_name(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Vui lòng nhập đầy đủ họ và tên')
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Mật khẩu phải dài từ 6 ký tự trở lên')
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.is_active = False
        user.set_password(validated_data['password'])
        user.save()
        return user
