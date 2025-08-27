# newforum/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User 
from rest_framework.permissions import IsAuthenticated
from .models import NewCommunityPost, NewCommunityComment
from .serializers import NewCommunityPostSerializer, NewCommunityCommentSerializer, CreateNewCommentSerializer


class NewCommunityPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get('createdBy', request.user.id)  # Obtener el user_id del cuerpo de la solicitud o usar el del usuario autenticado
            user = User.objects.get(id=user_id)
            post = NewCommunityPost.objects.create(
                title=request.data['title'],
                text=request.data['text'],
                createdBy=user
            )
            serializer = NewCommunityPostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user_id = request.query_params.get('user')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                posts = NewCommunityPost.objects.filter(createdBy=user).order_by('-createdAt')
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            posts = NewCommunityPost.objects.filter(createdBy=request.user).order_by('-createdAt')
        serializer = NewCommunityPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class NewCommunityPostDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, post_id):
        try:
            return NewCommunityPost.objects.get(id=post_id)
        except NewCommunityPost.DoesNotExist:
            return None

    def get(self, request, post_id):
        post_instance = self.get_object(post_id)
        if not post_instance:
            return Response(
                {"res": "Object with post id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = NewCommunityPostSerializer(post_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id):
        post_instance = self.get_object(post_id)
        if not post_instance:
            return Response(
                {"res": "Object with post id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data
        serializer = NewCommunityPostSerializer(instance=post_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post_instance = self.get_object(post_id)
        if not post_instance:
            return Response(
                {"res": "Object with post id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        post_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)
    
class NewCommunityCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        data = request.data
        data['post'] = post_id
        data['createdBy'] = request.user.id

        serializer = CreateNewCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, post_id):
        comments = NewCommunityComment.objects.filter(post=post_id, createdBy=request.user).order_by('-createdAt')
        serializer = NewCommunityCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NewCommunityCommentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, comment_id, user):
        try:
            return NewCommunityComment.objects.get(id=comment_id, createdBy=user)
        except NewCommunityComment.DoesNotExist:
            return None

    def get(self, request, post_id, comment_id):
        comment_instance = self.get_object(comment_id, request.user)
        if not comment_instance:
            return Response(
                {"res": "Object with comment id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = NewCommunityCommentSerializer(comment_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id, comment_id):
        comment_instance = self.get_object(comment_id, request.user)
        if not comment_instance:
            return Response(
                {"res": "Object with comment id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data
        serializer = NewCommunityCommentSerializer(instance=comment_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):
        comment_instance = self.get_object(comment_id, request.user)
        if not comment_instance:
            return Response(
                {"res": "Object with comment id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        comment_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)
