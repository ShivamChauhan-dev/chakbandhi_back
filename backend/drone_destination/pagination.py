from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPageNumberPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        next_page = None
        if self.page.has_next():
            next_page = self.page.next_page_number()

        previous_page = None
        if self.page.has_previous():
            previous_page = self.page.previous_page_number()

        return Response({
            'page': self.request.query_params.get('page', 1),
            'next_page': next_page,
            'next_page_link': self.get_next_link(),
            'previous_page': previous_page,
            'previous_page_link': self.get_previous_link(),
            'count': len(data),
            'max_pages': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,
            'data': data
        })


class StandardResultSetPagination(StandardPageNumberPagination):
    page_size = 10  # The default page size
    page_size_query_param = 'page_size'  # Custom page size
    max_page_size = 100
