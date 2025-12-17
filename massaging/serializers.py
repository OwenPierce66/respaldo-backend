# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Message,
    MessageAttachment,
    Group,
    GroupMembership,
    GroupMessage,
    GroupMessageAttachment,
)


class UserSerializer(serializers.ModelSerializer):
    """
    Usuario con campo de imagen listo para el chat.
    Ajusta los nombres de campos 'image', 'profile_image', 'avatar', 'image_profile'
    según tu modelo real de perfil/usuario.
    """
    image = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "image", "profile_image", "avatar"]

    def _get_any_image_field(self, obj):
        # 1) campos directos en User
        for attr in ["image", "profile_image", "avatar", "image_profile", "foto"]:
            if hasattr(obj, attr) and getattr(obj, attr):
                return getattr(obj, attr)

        # 2) perfil relacionado (User.profile, User.perfil, etc.)
        profile = getattr(obj, "profile", None) or getattr(obj, "perfil", None)
        if profile:
            for attr in ["image", "profile_image", "avatar", "image_profile", "foto"]:
                if hasattr(profile, attr) and getattr(profile, attr):
                    return getattr(profile, attr)

        return None

    def _build_url(self, file_field):
        if not file_field:
            return None
        request = self.context.get("request")
        url = file_field.url
        return request.build_absolute_uri(url) if request else url

    def get_image(self, obj):
        return self._build_url(self._get_any_image_field(obj))

    def get_profile_image(self, obj):
        return self.get_image(obj)

    def get_avatar(self, obj):
        return self.get_image(obj)


class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ["id", "file", "file_type", "is_image", "is_video"]


class GroupMessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessageAttachment
        fields = ["id", "file", "file_type", "is_image", "is_video"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)

    # respuesta a otro mensaje
    replied_to = serializers.SerializerMethodField()

    # campos top-level por compat con el front: msg.sender_image / msg.user_image
    sender_image = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "receiver",
            "content",
            "translated_content",
            "image",
            "video",
            "timestamp",
            "replied_to",
            "attachments",
            "sender_image",
            "user_image",
        ]

    def get_replied_to(self, obj):
        if not obj.replied_to:
            return None
        rep = obj.replied_to
        return {
            "id": rep.id,
            "content": rep.content,
            "sender": {
                "id": rep.sender.id,
                "username": rep.sender.username,
            },
            "timestamp": rep.timestamp,
        }

    def _get_sender_image_url(self, obj):
        user = obj.sender
        serializer = UserSerializer(user, context=self.context)
        # usa el mismo campo "image" del serializer
        return serializer.data.get("image")

    def get_sender_image(self, obj):
        return self._get_sender_image_url(obj)

    def get_user_image(self, obj):
        return self._get_sender_image_url(obj)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "created_at", "created_by"]


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ["id", "user", "group", "is_admin", "joined_at"]


class GroupMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    attachments = GroupMessageAttachmentSerializer(many=True, read_only=True)

    replied_to = serializers.SerializerMethodField()
    sender_image = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = GroupMessage
        fields = [
            "id",
            "group",
            "sender",
            "content",
            "image",
            "video",
            "timestamp",
            "replied_to",
            "attachments",
            "sender_image",
            "user_image",
        ]

    def get_replied_to(self, obj):
        if not obj.replied_to:
            return None
        rep = obj.replied_to
        return {
            "id": rep.id,
            "content": rep.content,
            "sender": {
                "id": rep.sender.id,
                "username": rep.sender.username,
            },
            "timestamp": rep.timestamp,
        }

    def _get_sender_image_url(self, obj):
        user = obj.sender
        serializer = UserSerializer(user, context=self.context)
        return serializer.data.get("image")

    def get_sender_image(self, obj):
        return self._get_sender_image_url(obj)

    def get_user_image(self, obj):
        return self._get_sender_image_url(obj)
