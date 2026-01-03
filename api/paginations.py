
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core import serializers


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        size = self.page_size
        if 'size' in self.request.GET:
            size = int(self.request.GET.get('size'))
        if (len(data) < size):
            size = len(data)
        return Response({
            # 'links': {
            #     'next': self.get_next_link(),
            #     'previous': self.get_previous_link()
            # },
            'pagination': {
                'page': self.page.number,
                'size': size,
                'count': self.page.paginator.count,
            },
            'data': data,
        })


class DefaultCustomPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        size = self.page_size
        if 'size' in self.request.GET:
            size = int(self.request.GET.get('size'))
        if (len(data) < size):
            size = len(data)
        return Response({
            # 'links': {
            #     'next': self.get_next_link(),
            #     'previous': self.get_previous_link()
            # },
            'pagination': {
                'page': self.page.number,
                'size': size,
                'count': self.page.paginator.count,
            },
            'data': data,
        })
