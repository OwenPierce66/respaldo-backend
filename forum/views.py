from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import ( CommunityPost, CommunityComment )
from .serializers import ( CommunityPostSerializer, CommunityCommentSerializer, CreateCommentSerializer )

class CommunityPostView(APIView):
  def post(self, request):
    try:
      CommunityPost.objects.create(
        title = request.data['title'],
        text = request.data['text'],
        createdBy = request.user
      )
      return Response({"success"},status=status.HTTP_200_OK)
    except:
      return Response({"Errors"}, status=status.HTTP_400_BAD_REQUEST)
  
  def get(self, request):
    posts = CommunityPost.objects.all().order_by('-createdAt')
    serializer = CommunityPostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class CommunityPostDetailsView(APIView):
  def get_object(self, post_id):
    try:
      return CommunityPost.objects.get(id=post_id)
    except CommunityPost.DoesNotExist:
      return None
  
  def get(self, request, post_id):
    post_instance = self.get_object(post_id)

    if not post_instance:
      return Response(
        {"res": "Object with lesson id does not exist"},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    serializer = CommunityPostSerializer(post_instance)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def put(self, request, post_id):
    post_instance = self.get_object(post_id)

    if not post_instance:
      return Response(
        {"res": "Object with lesson id does not exist"},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    data = {**request.data}

    serializer = CommunityPostSerializer(instance=post_instance, data=data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, post_id):
    post_instance = self.get_object(post_id)

    if not post_id:
      return Response(
        {"res": "Object with lesson id does not exist"},
        status=status.HTTP_400_BAD_REQUEST
      )

    post_instance.delete()
    return Response(
        {"res": "Object deleted!"},
        status=status.HTTP_200_OK
    )

class CommunityCommentView(APIView):
  def post(self, request, post_id):
    data = request.data
    serializer = CreateCommentSerializer(data=data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
  def get(self, request, post_id):
    posts = CommunityComment.objects.filter(post=post_id).order_by('-createdAt')
    serializer = CommunityCommentSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class CommunityCommentDetailsView(APIView):
  def get_object(self, comment_id):
    try:
      return CommunityComment.objects.get(id=comment_id)
    except CommunityComment.DoesNotExist:
      return None
  
  def get(self, request, post_id, comment_id):
    comment_instance = self.get_object(comment_id)

    if not comment_instance:
      return Response(
        {"res": "Object with lesson id does not exist"},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    serializer = CommunityCommentSerializer(comment_instance)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def put(self, request, post_id, comment_id):
    comment_instance = self.get_object(comment_id)

    if not comment_instance:
      return Response(
        {"res": "Object with lesson id does not exist"},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    data = {**request.data}

    serializer = CommunityCommentSerializer(instance=comment_instance, data=data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, post_id, comment_id):
    comment_instance = self.get_object(comment_id)

    if not post_id:
      return Response(
        {"res": "Object with lesson id does not exist"},
        status=status.HTTP_400_BAD_REQUEST
      )

    comment_instance.delete()
    return Response(
        {"res": "Object deleted!"},
        status=status.HTTP_200_OK
    )