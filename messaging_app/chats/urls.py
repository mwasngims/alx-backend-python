from django.urls import path, include
from rest_framework import routers as drf_routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet

# Base router for main resources
router = drf_routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages within a conversation
conversations_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),                # URLs for conversations
    path('', include(conversations_router.urls)),  # Nested URLs for messages within conversations
]
