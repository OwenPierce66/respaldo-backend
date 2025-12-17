# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Message,
    MessageLike,
    MessageAttachment,
    Group,
    GroupMembership,
    GroupMessage,
    GroupMessageAttachment,
)




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'file_type', 'is_image', 'is_video']


class GroupMessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessageAttachment
        fields = ['id', 'file', 'file_type', 'is_image', 'is_video']


# 👇 NUEVO: versión reducida del mensaje para usar en replied_to
class MessageReplySerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)

    likes_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    attachments = MessageAttachmentSerializer(many=True, read_only=True)

    # 👇 NUEVO: mensaje al que responde (solo lectura)
    replied_to = MessageReplySerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'content',
            'image',
            'translated_content',
            'video',
            'timestamp',
            'likes_count',
            'user_has_liked',
            'attachments',
            'replied_to',   # 👈 importante
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user_has_liked(self, obj):
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user'):
            return False
        user = request.user
        if not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    current_user_is_admin = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'created_at',
            'created_by',
            'members',
            'current_user_is_admin',
        ]

    def get_members(self, obj):
        memberships = GroupMembership.objects.filter(
            group=obj
        ).select_related('user')

        return [
            {
                "id": m.user.id,
                "username": m.user.username,
                "is_admin": m.is_admin,
                "is_creator": (obj.created_by_id == m.user_id),
            }
            for m in memberships
        ]

    def get_current_user_is_admin(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return False

        user = request.user

        if obj.created_by_id == user.id:
            return True

        return GroupMembership.objects.filter(
            group=obj,
            user=user,
            is_admin=True
        ).exists()


class GroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        fields = ['user', 'group', 'is_admin', 'joined_at']


# 👇 NUEVO: versión reducida para replied_to en grupos
class GroupMessageReplySerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = GroupMessage
        fields = ['id', 'sender', 'content', 'timestamp']


class GroupMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachments = GroupMessageAttachmentSerializer(many=True, read_only=True)
    # 👇 NUEVO
    replied_to = GroupMessageReplySerializer(read_only=True)

    class Meta:
        model = GroupMessage
        fields = [
            'id',
            'group',
            'sender',
            'content',
            'image',
            'video',
            'timestamp',
            'attachments',
            'replied_to',   # 👈 importante
        ]