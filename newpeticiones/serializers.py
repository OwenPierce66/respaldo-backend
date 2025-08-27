# newpeticiones/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import NewPeticionPost, NewPeticionComment
from api.serializers import UserSerializer

class NewPeticionPostSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer()

    class Meta:
        model = NewPeticionPost
        fields = "__all__"

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CreateNewPeticionCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewPeticionComment
        fields = "__all__"

class NewPeticionCommentSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer()
    children = RecursiveField(many=True)
    is_parent = serializers.ReadOnlyField()

    class Meta:
        model = NewPeticionComment
        fields = "__all__"
