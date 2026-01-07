from rest_framework import viewsets
from ..models import PhuongTienHuHong
from .serializers import PhuongTienHuHongSerializer

class PhuongTienHuHongViewSet(viewsets.ModelViewSet):
    queryset = PhuongTienHuHong.objects.all()
    serializer_class = PhuongTienHuHongSerializer


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
from django.db.models import Q, F, Count, Value, Sum, Case, When, IntegerField
from django.db import models


# views.py trong ViewSet của bạn
from rest_framework.decorators import action
from rest_framework.response import Response



class Text_to_speak(APIView):
    def get(self, request):
        text = request.query_params.get('text')
        return Response({'data': text_to_mp3(text)})
# Thống kê thực lực
class Thuc_luc(APIView):
    def get(self, request):
        # Filter params
        chung_loai = request.query_params.get('chung_loai')
        kho_nhap_id = request.query_params.get('kho_nhap')
        success_status = request.query_params.get('success', True)

        queryset = Chi_tiet_phieu_nhap.objects.all()

        # Build a list of all relevant kho_nhap (including children)
        if kho_nhap_id:
            try:
                target_kho = Danh_muc_kho.objects.get(id=kho_nhap_id)
                # Get all descendants of the target_kho
                descendant_kho_ids = [target_kho.id]  # Include the target kho itself

                # Recursive function to get all children
                def get_children_ids(kho_item):
                    for child in kho_item.children.all():
                        descendant_kho_ids.append(child.id)
                        get_children_ids(child)

                get_children_ids(target_kho)
                queryset = queryset.filter(phieu_nhap__kho_nhap__in=descendant_kho_ids)

            except Danh_muc_kho.DoesNotExist:
                return Response({'error': 'Kho nhập not found'}, status=status.HTTP_404_NOT_FOUND)

        # Filter by success status
        queryset = queryset.filter(phieu_nhap__success=success_status)

        # Annotate with import and export totals
        queryset = queryset.values('chung_loai__maso', 'chung_loai', 'ten').annotate(
            nhap_totals=Sum(
                Case(
                    When(phieu_nhap__kho_nhap__in=descendant_kho_ids, then='so_luong'),
                    default=Value(0),
                    output_field=models.IntegerField()
                )
            ),
            xuat_totals=Sum(
                Case(
                    When(phieu_nhap__kho_xuat__in=descendant_kho_ids, then='so_luong'),
                    default=Value(0),
                    output_field=models.IntegerField()
                )
            )
        ).annotate(
            totals=F('nhap_totals') - F('xuat_totals')
        ).filter(totals__gt=0).order_by('ten')

        # Filter by chung_loai
        if chung_loai:
            try:
                ma_so = Chung_loai.objects.get(id=chung_loai).maso
                queryset = queryset.filter(chung_loai__maso__icontains=ma_so)
            except Chung_loai.DoesNotExist:
                return Response({'error': 'Chủng loại not found'}, status=status.HTTP_404_NOT_FOUND)

        _count = queryset.count()
        _sum = queryset.aggregate(total_sum=Sum('totals'))['total_sum'] or 0

        return Response({'kho_nhap': kho_nhap_id, 'sum': _sum, 'count': _count, 'data': list(queryset)}, status=status.HTTP_200_OK)

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
    # views.py trong ViewSet của bạn
    @action(detail=False, methods=['post'])
    def bulk_create_chungloai(self, request):
        data = request.data  # Danh sách mảng từ Frontend gửi lên
        created_list = []
        
        for item in data:
            parent = None
            if item.get('parent_maso'):
                parent = Chung_loai.objects.filter(maso=item['parent_maso']).first()
            
            # Tạo đối tượng nhưng chưa lưu xuống DB ngay
            new_obj = Chung_loai(
                ten=item['ten'],
                parent=parent
            )
            # Lưu ý: Vì bạn có logic tự sinh mã số trong hàm save(), 
            # nên sử dụng .save() thay vì bulk_create để đảm bảo logic mã số được chạy đúng.
            new_obj.save() 
            created_list.append(new_obj.id)

        return Response({"status": "success", "count": len(created_list)})
    
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

