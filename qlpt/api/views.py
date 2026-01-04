from rest_framework import viewsets
from ..models import PhuongTien
from .serializers import PhuongTienSerializer

class PhuongTienViewSet(viewsets.ModelViewSet):
    queryset = PhuongTien.objects.all()
    serializer_class = PhuongTienSerializer






from datetime import datetime
# Import Serializer
from .serializers import Chung_loaiSerializer, Danh_muc_kho_Serializer, Danh_muc_nguon_cap_Serializer, Chi_tiet_phieu_nhap_Serializer, Phieu_nhap_Serializer
from .serializers import Tai_lieu_phuong_tien_Serializer
# Import Models
from qlpt.models import Tai_lieu_phuong_tien, File
from qlpt.models import Danh_muc_kho, Danh_muc_nguon_cap, Chi_tiet_phieu_nhap, Phieu_nhap, Chung_loai
from utils import text_to_mp3, get_queryset__datetime_filter

from api.permissions import IsPostOrAdmin, IsAuthenticatedOrReadOnly, ObjectPermission
from api.paginations import CustomPagination
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, permissions
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Count, Value, Sum



class Text_to_speak(APIView):
    def get(self, request):
        text = request.query_params.get('text')
        return Response({'data': text_to_mp3(text)})
# Thống kê thực lực
class Thuc_luc(APIView):
    def get(self, request):
        # Filter params
        chung_loai = request.query_params.get('chung_loai')
        kho_nhap = request.query_params.get('kho_nhap')
        success = request.query_params.get('success') or True
        parent = request.query_params.get('kho_nhap__parent') or 1
        kho_is_active = True
        if kho_nhap:
            parent = kho_nhap
            kho_is_active = Danh_muc_kho.objects.get(id=kho_nhap).active
        # Get queryset
        List_PT_nhap = Chi_tiet_phieu_nhap.objects.order_by('ten').filter(
                        Q(phieu_nhap__kho_nhap=parent) |
                        Q(phieu_nhap__kho_nhap__parent=parent) |
                        Q(phieu_nhap__kho_nhap__parent__parent=parent),
                        phieu_nhap__success=success,
                        phieu_nhap__kho_nhap__active=kho_is_active
                        ).exclude(
                        Q(phieu_nhap__kho_xuat=parent) |
                        Q(phieu_nhap__kho_xuat__parent=parent) |
                        Q(phieu_nhap__kho_xuat__parent__parent=parent)
                        ).values('chung_loai__maso','chung_loai', 'ten').annotate(totals = Sum('so_luong'))

        List_PT_xuat = Chi_tiet_phieu_nhap.objects.filter(
                        Q(phieu_nhap__kho_xuat=parent) |
                        Q(phieu_nhap__kho_xuat__parent=parent) |
                        Q(phieu_nhap__kho_xuat__parent__parent=parent),
                        phieu_nhap__success=success
                        ).exclude(
                        Q(phieu_nhap__kho_nhap=parent) |
                        Q(phieu_nhap__kho_nhap__parent=parent) |
                        Q(phieu_nhap__kho_nhap__parent__parent=parent)
                        ).values('chung_loai', 'ten').annotate(totals = Sum('so_luong'))
        # Filter by chung_loai
        if chung_loai:
            ma_so = Chung_loai.objects.get(id=chung_loai).maso
            List_PT_nhap=List_PT_nhap.filter(chung_loai__maso__icontains=ma_so)
            List_PT_xuat=List_PT_xuat.filter(chung_loai__maso__icontains=ma_so)
        # Merge data
        _count = 0
        _sum = 0
        for pt in List_PT_nhap:
            _xuat = List_PT_xuat.filter(chung_loai=pt['chung_loai'],ten=pt['ten'])
            if _xuat:
                pt['totals'] = pt['totals']-_xuat[0]['totals']
            if pt['totals']:
                _count = _count + 1
                _sum = _sum + pt['totals']
        return Response({'kho_nhap':kho_nhap,'sum': _sum, 'count': _count, 'data': List_PT_nhap}, status=status.HTTP_200_OK)

class Ton_kho(APIView):
    def get(self, request):
        def sapxetheoID(e):
            return e['id']
        if (request.query_params.get('export_from')):
            kho = request.query_params.get('export_from')
            List_PT_nhap = Chi_tiet_phieu_nhap.objects.filter(phieu_nhap__kho_nhap=kho,phieu_nhap__success=True).values('id','chung_loai', 'ten','nguon_cap','nam_cap','nguyen_gia',).annotate(totals = Sum('so_luong'))
            List_PT_xuat = Chi_tiet_phieu_nhap.objects.filter(phieu_nhap__kho_xuat=kho,phieu_nhap__success=True).values('chung_loai', 'ten','nguon_cap','nam_cap','nguyen_gia',).annotate(totals = Sum('so_luong'))
            _result = []
            for pt in List_PT_nhap:
                _xuat = List_PT_xuat.filter(chung_loai=pt['chung_loai'],ten=pt['ten'],nguon_cap=pt['nguon_cap'],nam_cap=pt['nam_cap'],nguyen_gia=pt['nguyen_gia'],)
                if _xuat:
                    pt['totals'] = pt['totals']-_xuat[0]['totals']
                _result.append(pt)
            _result.sort(key=sapxetheoID)
            return Response({'data': list(_result)}, status=status.HTTP_200_OK)
        return Response({'data': []}, status=status.HTTP_200_OK)

class Danh_muc_kho_viewSet(viewsets.ModelViewSet):
    queryset = Danh_muc_kho.objects.filter(parent__isnull=True)
    serializer_class = Danh_muc_kho_Serializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'active','id',]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class Danh_muc_nguon_cap_viewSet(viewsets.ModelViewSet):
    queryset = Danh_muc_nguon_cap.objects.all()
    serializer_class = Danh_muc_nguon_cap_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # permission_classes = [permissions.IsAuthenticated]

class Chung_loai_viewSet(viewsets.ModelViewSet):
    queryset = Chung_loai.objects.filter(parent__isnull=True)
    serializer_class = Chung_loaiSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent','children']
    
class Tai_lieu_phuong_tien_viewSet(viewsets.ModelViewSet):
    queryset = Tai_lieu_phuong_tien.objects.all()
    serializer_class = Tai_lieu_phuong_tien_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # permission_classes = [permissions.IsAuthenticated]

class Phieu_nhap_ViewSet(viewsets.ModelViewSet):
    queryset = Phieu_nhap.objects.all()
    serializer_class = Phieu_nhap_Serializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['kho_nhap', 'kho_xuat', 'thoi_gian', 'nguon_cap', 'quyetdinh', 'success',
                        'phuong_tiens__chung_loai', 'phuong_tiens__nguon_cap',
                        'phuong_tiens__ten']
    search_fields = ['phuong_tiens__ten']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return get_queryset__datetime_filter(self,Phieu_nhap.objects,'thoi_gian')

class Chi_tiet_phieu_nhap_ViewSet(viewsets.ModelViewSet):
    # List phiếu nhập có trạng thái success
    queryset = Chi_tiet_phieu_nhap.objects.all()
    serializer_class = Chi_tiet_phieu_nhap_Serializer
    pagination_class = CustomPagination
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['phieu_nhap', 'chung_loai',
    #                     'phieu_nhap__success', 'phieu_nhap__kho_nhap', 'phieu_nhap__nguon_cap']
    # search_fields = ['ten']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # permission_classes = [permissions.IsAuthenticated]

