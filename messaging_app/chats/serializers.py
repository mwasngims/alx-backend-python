from rest_framework import serializers
from .models import CustomUser, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model."""
    phone_number = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']

    def validate_message_body(self, value):
        """Raise error if message body is empty."""
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")  # ✅ Correct usage
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model including nested messages and participants."""
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']

    def get_messages(self, obj):
        """Return serialized messages for a conversation."""
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data

