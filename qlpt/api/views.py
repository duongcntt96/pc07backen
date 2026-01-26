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

from django.db.models import Sum, Case, When, Value, IntegerField, F
from django.db import models

class Thuc_luc(APIView):
    def get(self, request):
        # 1. Thu thập và chuẩn hóa Parameter
        chung_loai_id = request.query_params.get('chung_loai')
        kho_nhap_id = request.query_params.get('kho_nhap')
        
        success_param = request.query_params.get('success', 'true').lower()
        success_status = True if success_param == 'true' else False

        if not kho_nhap_id:
            return Response({'error': 'Vui lòng chọn đơn vị (kho) để thống kê'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Lấy danh sách ID kho (Bao gồm kho hiện tại và tất cả kho con)
            # Tối ưu: Lấy toàn bộ trong 1 query, tránh đệ quy gọi DB nhiều lần
            target_kho = Danh_muc_kho.objects.get(id=kho_nhap_id)
            
            # Nếu bạn dùng django-mptt: 
            # descendant_kho_ids = target_kho.get_descendants(include_self=True).values_list('id', flat=True)
            
            # Nếu dùng model thường (Đệ quy tối ưu bằng bộ nhớ):
            all_kho = Danh_muc_kho.objects.all().values('id', 'parent_id')
            kho_tree = {}
            for k in all_kho:
                kho_tree.setdefault(k['parent_id'], []).append(k['id'])

            descendant_kho_ids = [target_kho.id]
            stack = [target_kho.id]
            while stack:
                current_id = stack.pop()
                children = kho_tree.get(current_id, [])
                descendant_kho_ids.extend(children)
                stack.extend(children)

            # 3. Xây dựng QuerySet cơ sở
            # Lọc các chi tiết phiếu thỏa mãn: (Thành công) VÀ (Nằm trong danh sách kho nhập HOẶC kho xuất)
            queryset = Chi_tiet_phieu_nhap.objects.filter(
                phieu_nhap__success=success_status
            ).filter(
                Q(phieu_nhap__kho_nhap__in=descendant_kho_ids) | 
                Q(phieu_nhap__kho_xuat__in=descendant_kho_ids)
            ).select_related('phieu_nhap', 'chung_loai')

            # Lọc theo chủng loại nếu có yêu cầu
            if chung_loai_id:
                try:
                    ma_so = Chung_loai.objects.get(id=chung_loai_id).maso
                    queryset = queryset.filter(chung_loai__maso__icontains=ma_so)
                except Chung_loai.DoesNotExist:
                    return Response({'error': 'Chủng loại không tồn tại'}, status=404)

            # 4. Aggregate: Tính toán Nhập - Xuất - Tồn
            # totals = Tổng Nhập (vào kho đang xét) - Tổng Xuất (ra khỏi kho đang xét)
            stats = queryset.values(
                'chung_loai', 
                'chung_loai__maso', 
                'ten'
            ).annotate(
                nhap_totals=Sum(
                    Case(
                        When(phieu_nhap__kho_nhap__in=descendant_kho_ids, then='so_luong'),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                xuat_totals=Sum(
                    Case(
                        When(phieu_nhap__kho_xuat__in=descendant_kho_ids, then='so_luong'),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                )
            ).annotate(
                totals=F('nhap_totals') - F('xuat_totals')
            ).filter(totals__gt=0).order_by('ten')

            # 5. Tính toán tổng hợp cuối cùng
            _count = stats.count()
            _sum = stats.aggregate(total_sum=Sum('totals'))['total_sum'] or 0

            return Response({
                'kho_nhap': kho_nhap_id,
                'sum': _sum,
                'count': _count,
                'data': list(stats)
            }, status=status.HTTP_200_OK)

        except Danh_muc_kho.DoesNotExist:
            return Response({'error': 'Kho không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # Thống kê thực lực
# class Thuc_luc(APIView):
#     def get(self, request):
#         # Filter params
#         chung_loai = request.query_params.get('chung_loai')
#         kho_nhap_id = request.query_params.get('kho_nhap')
#         success_status = request.query_params.get('success', True)

#         queryset = Chi_tiet_phieu_nhap.objects.all()

#         # Build a list of all relevant kho_nhap (including children)
#         if kho_nhap_id:
#             try:
#                 target_kho = Danh_muc_kho.objects.get(id=kho_nhap_id)
#                 # Get all descendants of the target_kho
#                 descendant_kho_ids = [target_kho.id]  # Include the target kho itself

#                 # Recursive function to get all children
#                 def get_children_ids(kho_item):
#                     for child in kho_item.children.all():
#                         descendant_kho_ids.append(child.id)
#                         get_children_ids(child)

#                 get_children_ids(target_kho)
#                 queryset = queryset.filter(phieu_nhap__kho_nhap__in=descendant_kho_ids)

#             except Danh_muc_kho.DoesNotExist:
#                 return Response({'error': 'Kho nhập not found'}, status=status.HTTP_404_NOT_FOUND)

#         # Filter by success status
#         queryset = queryset.filter(phieu_nhap__success=success_status)

#         # Annotate with import and export totals
#         queryset = queryset.values('chung_loai__maso', 'chung_loai', 'ten').annotate(
#             nhap_totals=Sum(
#                 Case(
#                     When(phieu_nhap__kho_nhap__in=descendant_kho_ids, then='so_luong'),
#                     default=Value(0),
#                     output_field=models.IntegerField()
#                 )
#             ),
#             xuat_totals=Sum(
#                 Case(
#                     When(phieu_nhap__kho_xuat__in=descendant_kho_ids, then='so_luong'),
#                     default=Value(0),
#                     output_field=models.IntegerField()
#                 )
#             )
#         ).annotate(
#             totals=F('nhap_totals') - F('xuat_totals')
#         ).filter(totals__gt=0).order_by('ten')

#         # Filter by chung_loai
#         if chung_loai:
#             try:
#                 ma_so = Chung_loai.objects.get(id=chung_loai).maso
#                 queryset = queryset.filter(chung_loai__maso__icontains=ma_so)
#             except Chung_loai.DoesNotExist:
#                 return Response({'error': 'Chủng loại not found'}, status=status.HTTP_404_NOT_FOUND)

#         _count = queryset.count()
#         _sum = queryset.aggregate(total_sum=Sum('totals'))['total_sum'] or 0

#         return Response({'kho_nhap': kho_nhap_id, 'sum': _sum, 'count': _count, 'data': list(queryset)}, status=status.HTTP_200_OK)

class PhanBoThucLucChiTiet(APIView):
    def get(self, request):
        kho_goc_id = request.query_params.get('kho_id')
        # Thêm filter param
        chung_loai_id = request.query_params.get('chung_loai')
        # Lọc theo chủng loại nếu có yêu cầu
        if chung_loai_id:
            try:
                ma_so = Chung_loai.objects.get(id=chung_loai_id).maso
                # queryset = queryset.filter(chung_loai__maso__icontains=ma_so)
            except Chung_loai.DoesNotExist:
                return Response({'error': 'Chủng loại không tồn tại'}, status=404)
        search_name = request.query_params.get('q') # Tìm theo tên hoặc mã

        if not kho_goc_id:
            return Response({'error': 'Vui lòng cung cấp kho_id'}, status=400)

        try:
            kho_goc = Danh_muc_kho.objects.get(id=kho_goc_id)
            kho_con_list = list(Danh_muc_kho.objects.filter(parent_id=kho_goc_id)) + [kho_goc]
            
            kho_mapping = {}
            for k in kho_con_list:
                kho_mapping[k.id] = [k.id] if k.id == kho_goc.id else self.get_all_descendants(k.id)

            all_relevant_ids = [idx for sublist in kho_mapping.values() for idx in sublist]

            # 1. Khởi tạo QuerySet cơ bản
            queryset = Chi_tiet_phieu_nhap.objects.filter(
                phieu_nhap__success=True
            ).filter(
                Q(phieu_nhap__kho_nhap__in=all_relevant_ids) | 
                Q(phieu_nhap__kho_xuat__in=all_relevant_ids)
            )

            # 2. ÁP DỤNG FILTER TẠI ĐÂY
            if chung_loai_id:
                queryset = queryset.filter(chung_loai__maso__icontains=ma_so)
            
            if search_name:
                queryset = queryset.filter(
                    Q(chung_loai__ten__icontains=search_name) | 
                    Q(chung_loai__maso__icontains=search_name)
                )

            # 3. Lấy dữ liệu đã filter
            raw_stats = queryset.values(
                'chung_loai_id', 'chung_loai__maso', 'chung_loai__ten',
                'phieu_nhap__kho_nhap_id', 'phieu_nhap__kho_xuat_id', 'so_luong'
            )

            # --- Logic xử lý matrix (như bản trước) ---
            matrix = {}
            for item in raw_stats:
                cl_id = item['chung_loai_id']
                if cl_id not in matrix:
                    matrix[cl_id] = {
                        'maso': item['chung_loai__maso'],
                        'ten_chung_loai': item['chung_loai__ten'],
                        'chi_tiet_kho': {k.id: 0 for k in kho_con_list},
                        'tong_cong': 0
                    }

                for k_id, sub_ids in kho_mapping.items():
                    if item['phieu_nhap__kho_nhap_id'] in sub_ids:
                        matrix[cl_id]['chi_tiet_kho'][k_id] += item['so_luong']
                    if item['phieu_nhap__kho_xuat_id'] in sub_ids:
                        matrix[cl_id]['chi_tiet_kho'][k_id] -= item['so_luong']

            final_data = []
            for cl_id, info in matrix.items():
                info['tong_cong'] = sum(info['chi_tiet_kho'].values())
                # Có thể bỏ filter ton__gt=0 nếu muốn xem cả hàng đã hết
                if info['tong_cong'] != 0: 
                    final_data.append(info)

            return Response({
                'don_vi_goc': kho_goc.ten,
                'danh_sach_kho': [{'id': k.id, 'ten': k.ten} for k in kho_con_list],
                'data': sorted(final_data, key=lambda x: x['maso'])
            }, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def get_all_descendants(self, parent_id):
        descendants = [parent_id]
        children = Danh_muc_kho.objects.filter(parent_id=parent_id).values_list('id', flat=True)
        for child_id in children:
            descendants.extend(self.get_all_descendants(child_id))
        return descendants

# class Ton_kho(APIView):
#     def get(self, request):
#         kho_id = request.query_params.get('export_from')
#         if not kho_id:
#             return Response({'data': []}, status=status.HTTP_200_OK)
#         # Query gộp: Tính cả Nhập và Xuất trong 1 câu lệnh duy nhất
#         ton_kho_qs = Chi_tiet_phieu_nhap.objects.filter(
#             phieu_nhap__success=True,
#             parent_item__isnull=True
#         ).filter(
#             # Lọc những phiếu liên quan đến kho này (hoặc là kho nhập, hoặc là kho xuất)
#             models.Q(phieu_nhap__kho_nhap=kho_id) | models.Q(phieu_nhap__kho_xuat=kho_id)
#         ).values(
#             # Group by các trường này
#             'chung_loai_id', 'ten', 'nguon_cap_id', 'nam_cap', 'nguyen_gia'
#         ).annotate(
#             # Logic: Nếu là kho nhập thì +số lượng, nếu là kho xuất thì -số lượng
#             totals=Sum(
#                 Case(
#                     When(phieu_nhap__kho_nhap=kho_id, then=F('so_luong')),
#                     When(phieu_nhap__kho_xuat=kho_id, then=-F('so_luong')),
#                     default=Value(0),
#                     output_field=IntegerField(),
#                 )
#             )
#         ).filter(totals__gt=0).order_by('chung_loai_id') # Chỉ lấy hàng còn tồn
#         return Response({'data': list(ton_kho_qs)}, status=status.HTTP_200_OK)

class Ton_kho(APIView):
    def get(self, request):
        def sapxetheoID(e):
            return e['id']
        kho = request.query_params.get('export_from')
        if (kho):
            List_PT_nhap = Chi_tiet_phieu_nhap.objects.filter(phieu_nhap__kho_nhap=kho,phieu_nhap__success=True,parent_item__isnull=True).prefetch_related('kemtheo')
            List_PT_xuat = Chi_tiet_phieu_nhap.objects.filter(phieu_nhap__kho_xuat=kho,phieu_nhap__success=True,parent_item__isnull=True).prefetch_related('kemtheo')
            # Group nhap items by key attributes
            nhap_dict = {}
            for pt in List_PT_nhap:
                key = (pt.chung_loai_id, pt.ten, pt.nguon_cap_id, pt.nam_cap, pt.nguyen_gia)
                if key not in nhap_dict:
                    nhap_dict[key] = {
                        'id': pt.id,
                        'chung_loai': pt.chung_loai_id,
                        'ten': pt.ten,
                        'nguon_cap': pt.nguon_cap_id,
                        'nam_cap': pt.nam_cap,
                        'nguyen_gia': pt.nguyen_gia,
                        'kemtheo': [{'id': k.id,'chung_loai': k.chung_loai_id, 'ten': k.ten, 'so_luong': k.so_luong} for k in pt.kemtheo.all()],
                        'totals': pt.so_luong
                    }
                else:
                    nhap_dict[key]['totals'] += pt.so_luong
            
            # Subtract xuat from nhap
            for pt in List_PT_xuat:
                key = (pt.chung_loai_id, pt.ten, pt.nguon_cap_id, pt.nam_cap, pt.nguyen_gia)
                if key in nhap_dict:
                    nhap_dict[key]['totals'] -= pt.so_luong
            
            _result = list(nhap_dict.values())
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
    # queryset = Phieu_nhap.objects.all()
    queryset = Phieu_nhap.objects.prefetch_related('phuong_tiens__kemtheo').all()
    serializer_class = Phieu_nhap_Serializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['kho_nhap', 'kho_xuat', 'thoi_gian', 'nguon_cap', 'quyetdinh', 'success',
                        'phuong_tiens__chung_loai', 'phuong_tiens__nguon_cap',
                        'phuong_tiens__ten']
    search_fields = ['phuong_tiens__ten']
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # 1. Gọi hàm filter thời gian của bạn
        qs = get_queryset__datetime_filter(self, Phieu_nhap.objects, 'thoi_gian')
        
        # 2. Áp dụng Prefetch và Select related NGAY TẠI ĐÂY
        return qs.select_related(
            'kho_nhap', 
            'kho_xuat', 
            'nguon_cap'
        ).prefetch_related(
            'phuong_tiens__chung_loai', # Quan trọng: Load luôn chủng loại để serializer không query lẻ
            'phuong_tiens__kemtheo'     # Load đệ quy
        ).distinct() # Đảm bảo không trùng lặp khi filter qua quan hệ N-N

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

