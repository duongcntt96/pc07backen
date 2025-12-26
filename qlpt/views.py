from rest_framework import viewsets
from .models import PhuongTien
from .serializers import PhuongTienSerializer

class PhuongTienViewSet(viewsets.ModelViewSet):
    queryset = PhuongTien.objects.all()
    serializer_class = PhuongTienSerializer