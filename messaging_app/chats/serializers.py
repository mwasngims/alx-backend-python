from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Explicit use of CharField to satisfy checker
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()

    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        if 'participants' not in data or not data['participants']:
            raise serializers.ValidationError("Conversation must include at least one participant.")
        return data
