from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Conversation, Message
from .permissions import IsParticipantOfConversation
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations for conversations.
    """
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] 
    search_fields = ['participants__username']
    ordering_fields = ['created_at']
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        participants = request.data.get('participants', [])
        if not participants or not isinstance(participants, list):
            return Response({'error': 'Participants must be a list of user IDs.'}, status=status.HTTP_400_BAD_REQUEST)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides CRUD operations for messages within conversations.
    """
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            if self.request.user not in conversation.participants.all():
                # User is not participant, forbid access
                from rest_framework.status import HTTP_403_FORBIDDEN
                raise PermissionDenied(detail="You do not have permission to view messages for this conversation.", code=HTTP_403_FORBIDDEN)
            return Message.objects.filter(conversation=conversation)
        # If no conversation_id specified, return all messages user can see
        return Message.objects.filter(conversation__participants=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation')
        if not conversation_id:
            return Response({'error': 'Conversation ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            from rest_framework.status import HTTP_403_FORBIDDEN
            return Response({'detail': 'You do not have permission to send messages to this conversation.'}, status=HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
