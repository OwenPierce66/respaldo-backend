# newpeticiones/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import NewPeticionPost, NewPeticionComment
from .serializers import NewPeticionPostSerializer, NewPeticionCommentSerializer, CreateNewPeticionCommentSerializer

class NewPeticionPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get('createdBy', request.user.id)
            user = User.objects.get(id=user_id)
            post = NewPeticionPost.objects.create(
                title=request.data['title'],
                text=request.data['text'],
                createdBy=user
            )
            serializer = NewPeticionPostSerializer(post)
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
                posts = NewPeticionPost.objects.filter(createdBy=user).order_by('-createdAt')
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            posts = NewPeticionPost.objects.filter(createdBy=request.user).order_by('-createdAt')
        serializer = NewPeticionPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NewPeticionPostDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, peticion_id):
        try:
            return NewPeticionPost.objects.get(id=peticion_id)
        except NewPeticionPost.DoesNotExist:
            return None

    def get(self, request, peticion_id):
        peticion_instance = self.get_object(peticion_id)
        if not peticion_instance:
            return Response(
                {"res": "Object with peticion id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = NewPeticionPostSerializer(peticion_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, peticion_id):
        peticion_instance = self.get_object(peticion_id)
        if not peticion_instance:
            return Response(
                {"res": "Object with peticion id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data
        serializer = NewPeticionPostSerializer(instance=peticion_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, peticion_id):
        peticion_instance = self.get_object(peticion_id)
        if not peticion_instance:
            return Response(
                {"res": "Object with peticion id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        peticion_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)

class NewPeticionCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, peticion_id):
        data = request.data
        data['post'] = peticion_id
        data['createdBy'] = request.user.id

        serializer = CreateNewPeticionCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, peticion_id):
        comments = NewPeticionComment.objects.filter(post=peticion_id, createdBy=request.user).order_by('-createdAt')
        serializer = NewPeticionCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NewPeticionCommentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, comment_id, user):
        try:
            return NewPeticionComment.objects.get(id=comment_id, createdBy=user)
        except NewPeticionComment.DoesNotExist:
            return None

    def get(self, request, peticion_id, comment_id):
        comment_instance = self.get_object(comment_id, request.user)
        if not comment_instance:
            return Response(
                {"res": "Object with comment id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = NewPeticionCommentSerializer(comment_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, peticion_id, comment_id):
        comment_instance = self.get_object(comment_id, request.user)
        if not comment_instance:
            return Response(
                {"res": "Object with comment id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data
        serializer = NewPeticionCommentSerializer(instance=comment_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, peticion_id, comment_id):
        comment_instance = self.get_object(comment_id, request.user)
        if not comment_instance:
            return Response(
                {"res": "Object with comment id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        comment_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)
