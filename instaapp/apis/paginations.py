from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Pagination class that splits the movie list into pages."""
    page_size = 2