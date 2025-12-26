from rest_framework import serializers
from .models import PhuongTien

class PhuongTienSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhuongTien
        fields = '__all__'
