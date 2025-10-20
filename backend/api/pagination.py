from rest_framework.pagination import PageNumberPagination

from backend.constants import DEFAULT_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация для API."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
