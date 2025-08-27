from rest_framework import serializers
from django.contrib.auth.models import User
from .models import NewCommunityPost, NewCommunityComment
from api.serializers import UserSerializer

class NewCommunityPostSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer()

    class Meta:
        model = NewCommunityPost
        fields = "__all__"

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CreateNewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewCommunityComment
        fields = "__all__"

class NewCommunityCommentSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer()
    children = RecursiveField(many=True)
    is_parent = serializers.ReadOnlyField()

    class Meta:
        model = NewCommunityComment
        fields = "__all__"