# chats/permissions.py

from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows access only to participants of a conversation.
    Assumes the view has a `.get_object()` method returning a Message or Conversation
    with sender and receiver or participants.
    """

    def has_permission(self, request, view):
        # Must be authenticated for all methods
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Allow access only if user is part of the conversation
        is_participant = False

        if hasattr(obj, "participants"):
            is_participant = user in obj.participants.all()
        elif hasattr(obj, "sender") and hasattr(obj, "receiver"):
            is_participant = user == obj.sender or user == obj.receiver

        if request.method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            return is_participant

        return False
