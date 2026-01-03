from rest_framework.response import Response
from rest_framework import viewsets

from api.paginations import CustomPagination

from user.models import bo_phan, cap_bac, chuc_vu, thong_tin_ca_nhan
from django.contrib.auth.models import User, Group

from .serializers import cap_bac_Serializer, chuc_vu_Serializer, bo_phan_Serializer, UserProfileSerializer, UserSerializer, GroupSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

class cap_bac_ViewSet(viewsets.ModelViewSet):
    queryset = cap_bac.objects.all()
    serializer_class = cap_bac_Serializer
    pagination_class = CustomPagination


class chuc_vu_ViewSet(viewsets.ModelViewSet):
    queryset = chuc_vu.objects.all()
    serializer_class = chuc_vu_Serializer
    pagination_class = CustomPagination

    
class bo_phan_ViewSet(viewsets.ModelViewSet):
    queryset = bo_phan.objects.all()
    serializer_class = bo_phan_Serializer
    pagination_class = CustomPagination


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = thong_tin_ca_nhan.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["team","chuc_vu","cap_bac","active"]
    search_fields = ["ten", "username__username"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = CustomPagination


class RegisterAPIView(APIView):

    def post(self, request):
        from .serializers import UserSerializer
        user = UserSerializer(data=request.data)
        if (user.is_valid()):
            user.save()
            return Response(user.data, status=status.HTTP_201_CREATED)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
