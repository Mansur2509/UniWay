from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CompactListPagination(PageNumberPagination):
    """Tighter cap for lists that are personal/curated (a handful of items in
    practice) rather than catalog-sized, so a caller can't force an
    expensive-to-serialize endpoint to return an unbounded page.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50

