# chats/pagination.py

from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.

    This class paginates messages in sets of 20 per page.
    The paginated response includes:
    - page.paginator.count: total number of messages
    - page.has_next(), page.has_previous(): navigation helpers
    """
    page_size = 20  # Fetch 20 messages per page
    page_size_query_param = 'page_size'
    max_page_size = 100
