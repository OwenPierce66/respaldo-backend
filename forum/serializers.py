from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import *
from api.serializers import UserSerializer

class CommunityPostSerializer(serializers.ModelSerializer):
  createdBy = UserSerializer()
  
  class Meta:
    model = CommunityPost
    fields = "__all__"
  
  def create(self, validated_data):
    instance = CommunityPost.objects.create(**validated_data)
    return instance

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommunityCommentSerializer(serializers.ModelSerializer):
  createdBy = UserSerializer()
  children = RecursiveField(many=True)
  is_parent = serializers.ReadOnlyField()

  class Meta:
    model = CommunityComment
    fields = "__all__"

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
      model = CommunityComment
      fields = "__all__"