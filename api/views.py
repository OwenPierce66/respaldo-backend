from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from datetime import datetime
from datetime import timedelta
from django.core.files.base import ContentFile
from django.db.models import Q
from django.conf import settings
import uuid
import json
import requests
import random
import string
import base64

from .models import (
    CalendarEventCategory, Token, Post, RaffleEntry, PetitionEntry, Upload, Petition,
    AgreementSubmission, Blog, Thumbnail, Blog, 
    RepresentativeSurveyEntry, CredencialSurveyEntry, VotingForAmmonSurveyEntry,
    Currency, Directory, BusinessPage, BusinessPagePost, BusinessPagePhoto, StripeCustomer,
    YOI_Assistant, CalendarEvent, Group, GroupMessage, YOI_Registration,
    CalendarEvent, Listing, VehicleListing, ListingImage, ClassifiedFavorite, ProfileImage
    )   
    
from .serializers import (
    CalendarEventCategorySerializer, SignUpSerializer, UserSerializer,PostSerializer,
    PetitionEntrySerializer, PetitionEntryGETSerializer,
    AgreementSubmissionSerializer, BlogSerializer, BlogPOSTSerializer,
    CurrencySerializer, DirectorySerializer, BusinessPageSerializer,
    BusinessPagePostSerializer, StripeCustomerSerializer, CalendarEventSerializer,
    YOI_AssistantSerializer, GroupSerializer, GroupMessageSerializer, 
    GroupCreateSerializer, GroupCreateMessageSerializer, YOI_RegistrationSerializer,
    ListingSerializer, VehicleListingSerializer, RaffleEntrySerializer,
    ClassifiedFavoriteSerializer,
    )

from .permissions import isEditorOrAdminPermission
from django.contrib.auth.models import User
from .utils import (
    create_stripe_payment, 
    create_error, 
    send_forgot_password_email, 
    reset_password,
    get_subscription
    )
from .pagination import SmallResultsSetPagination

import stripe

from django.core.mail import send_mail

from django.db.models import Count
from django.http import JsonResponse
from decouple import config



from .models import (
    Task, Like, Comment, Postt, ImagenFija, Portada, ForumPostt, LikeCommentPost, NewPeticionCommentPost, LikeP,NuevoTask, SharedTask, Favorito, pFavorito, Hashtag, CategoryP, NewCategory,  Imagen, TuModelo, Profile
    )   

from .serializers import (
    ImagenSerializer, LikeSerializer, SubFuentesPCHPostSerializer, SubFactoresPCHPostSerializer, ImagenFijaSerializer, PortadaSerializer, UserDetailsSerializer, SubFuentesSerializer, SubFactoresSerializer, SubTaskCommentPostSerializer, SubFuentesCommentPostSerializer, SubFactoresCommentPostSerializer, CreateNewPeticionCommentSerializer, NewPeticionCommentSerializer, PosttSerializer, SharedTaskCreateSerializer, SharedTaskSerializer, FavoritoReadSerializer, FavoritoSerializer, pFavoritoSerializer, CustomUserDetailsSerializer, NewCategorySerializer, CategoryPSerializer, SimpleUserSerializer, LikeCommentSerializer, TaskSerializer, NuevoTaskSerializer, TuModeloSerializer, SubTaskSerializer,
    )

from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework import viewsets
from rest_framework import generics, permissions
from .models import ForumPostt



# Vista para listar y crear portadas

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_who_shared_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        shared_tasks = SharedTask.objects.filter(task=task).select_related('shared_by')
        users = [shared_task.shared_by for shared_task in shared_tasks]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)
    except Task.DoesNotExist:
        return Response({'error': 'Tarea no encontrada'}, status=404)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def portada_list_create(request):
    if request.method == 'GET':
        portadas = Portada.objects.filter(user=request.user)
        serializer = PortadaSerializer(portadas, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PortadaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_task_with_images(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    serializer = TaskSerializer(task)
    
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def imagen_fija_list_create(request):
    if request.method == 'GET':
        imagen_fija = ImagenFija.objects.filter(user=request.user).last()
        if imagen_fija:
            serializer = ImagenFijaSerializer(imagen_fija)
            return Response(serializer.data)
        return Response({'detail': 'No hay imágenes fijas disponibles'}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'POST':
        print("request.FILES:", request.FILES)
        print("request.data:", request.data)
        serializer = ImagenFijaSerializer(data=request.data)
        if serializer.is_valid():
            imagen_fija = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Errores del serializer:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def portada_update_delete(request, portada_id):
    try:
        portada = Portada.objects.get(pk=portada_id)
    except Portada.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PortadaSerializer(portada, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        portada.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_portadas_usuario(request, user_id):
    try:
        portadas = Portada.objects.filter(user__id=user_id)
        serializer = PortadaSerializer(portadas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Portada.DoesNotExist:
        return Response({'detail': 'No se encontraron portadas para este usuario.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_imagen_fija_usuario(request, user_id):
    try:
        imagen_fija = ImagenFija.objects.filter(user__id=user_id).last()
        if imagen_fija:
            serializer = ImagenFijaSerializer(imagen_fija)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'No se encontró imagen fija para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
    except ImagenFija.DoesNotExist:
        return Response({'detail': 'No se encontró imagen fija para este usuario.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_portadas_usuario(request, user_id):
    try:
        portadas = Portada.objects.filter(user__id=user_id)
        if portadas.exists():
            serializer = PortadaSerializer(portadas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No se encontraron portadas para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_profile(request):
    user = request.user
    serializer = UserDetailsSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_profile(request):
    try:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"error": "No se pudo obtener el perfil del usuario"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny]) 
def users_who_liked_comment(request, comment_id):
    try:
        comment = NewPeticionCommentPost.objects.prefetch_related('likes').get(id=comment_id)
        users = [like.user for like in comment.likes.all()]
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except NewPeticionCommentPost.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list_create(request):
    if request.method == 'GET':
        posts = Postt.objects.filter(parent=None).order_by('-created_at')
        serializer = PosttSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PosttSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_shared_task(request):
    if request.method == 'POST':
        data = request.data.copy()
        task_id = data.get('task_id')

        if not task_id:
            return Response({"error": "Task ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        shared_by = request.user
        data['task'] = task.id
        data['shared_by'] = shared_by.pk

        serializer = SharedTaskCreateSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save(shared_by=shared_by, task=task)
            task.share_count += 1
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        shared_tasks = SharedTask.objects.all()
        serializer = SharedTaskSerializer(shared_tasks, many=True, context={'request': request})
        return Response(serializer.data)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_shared_task(request, shared_task_id):
    try:
        shared_task = SharedTask.objects.get(id=shared_task_id)
        shared_task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except SharedTask.DoesNotExist:
        return Response({"error": "SharedTask not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_favoritos_usuario(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user

    favoritos = Favorito.objects.filter(user=user)
    favoritos_ids = favoritos.values_list('task__id', flat=True)

    return Response(favoritos_ids, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_favorito(request):
    task_id = request.data.get('task')
    user = request.user

    if not task_id:
        return Response({'error': 'ID de tarea es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    task = get_object_or_404(Task, id=task_id)
    favorito_existente = Favorito.objects.filter(user=user, task=task).first()

    if favorito_existente:
        favorito_existente.delete()
        return Response({'mensaje': 'Favorito eliminado'}, status=status.HTTP_204_NO_CONTENT)
    else:
        Favorito.objects.create(user=user, task=task)
        return Response({'mensaje': 'Favorito agregado'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_favoritos(request):
    if request.method == 'GET':
        favoritos = Favorito.objects.filter(user=request.user)
        serializer = FavoritoReadSerializer(favoritos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = FavoritoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_favorito(request, task_id):
    user = request.user

    task = get_object_or_404(Task, id=task_id)
    favorito = Favorito.objects.filter(user=user, task=task).first()

    if favorito:
        favorito.delete()
        return Response({'mensaje': 'Favorito eliminado'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'error': 'El favorito no existe'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_pfavorito(request):
    perfil_id = request.data.get('perfil_id')
    try:
        perfil = User.objects.get(pk=perfil_id) 
    except User.DoesNotExist:
        return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    favorito_existente = pFavorito.objects.filter(user=request.user, perfil=perfil).first()
    
    if favorito_existente:
        favorito_existente.delete()
        return Response({'mensaje': 'Perfil eliminado de favoritos'}, status=status.HTTP_204_NO_CONTENT)
    else:
        pFavorito.objects.create(user=request.user, perfil=perfil)
        return Response({'mensaje': 'Perfil agregado a favoritos'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pfavoritos(request):
    favoritos = pFavorito.objects.filter(user=request.user)
    serializer = SimpleUserSerializer([fav.perfil for fav in favoritos], many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pfavoritos_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    favoritos = pFavorito.objects.filter(user=usuario)

    serializer = SimpleUserSerializer([fav.perfil for fav in favoritos], many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    serializer = CustomUserDetailsSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_admin(request):
    if not request.user.is_staff:
        return Response({"detail": "No tienes permiso para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
    
    return Response({"is_admin": True}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def new_category_list_create(request):
    if request.method == 'GET':
        categories = NewCategory.objects.all()
        serializer = NewCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_staff:
            return Response({"detail": "No tienes permiso para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = NewCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def new_category_detail_update_delete(request, pk):
    category = get_object_or_404(NewCategory, pk=pk)
    
    if request.method == 'GET':
        serializer = NewCategorySerializer(category)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'DELETE']:
        if not request.user.is_staff:
            return Response({"detail": "No tienes permiso para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = NewCategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_likes(request, profile_id):
    profile = get_object_or_404(User, pk=profile_id)
    likes = LikeP.objects.filter(profile=profile)
    liked_users = [like.user for like in likes]
    serializer = SimpleUserSerializer(liked_users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.all()
    serializer = SimpleUserSerializer(users, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_unlike_profile(request, profile_id):
    profile = get_object_or_404(User, pk=profile_id)
    like, created = LikeP.objects.get_or_create(user=request.user, profile=profile)
    if not created:
        like.delete()
        return Response({'status': 'like removed'})
    return Response({'status': 'like added'})

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([AllowAny])
def create_categoryp(request):
    if request.method == 'GET':
        categories = CategoryP.objects.filter(user=request.user)
        serializer = CategoryPSerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategoryPSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_categoryp(request, pk):
    if request.method == 'DELETE':
        categoria = get_object_or_404(CategoryP, pk=pk, user=request.user)
        categoria.delete()
        return Response(status=204)

@api_view(['GET'])
@permission_classes([AllowAny])
def ListUsersView(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = SimpleUserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

    
@api_view(['GET', 'PUT', 'DELETE', 'POST'])
def TuModeloListCreateView(request):
    if request.method == 'GET':
        tasks = TuModelo.objects.all()
        serializer = TuModeloSerializer(tasks, many=True)
        return Response(serializer.data)


    elif request.method == 'POST':
        serializer = TuModeloSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE', 'POST'])
def TuModeloRetrieveUpdateDestroyView(request):
    queryset = TuModelo.objects.all()
    serializer_class = TuModeloSerializer
    if request.method == 'GET':
        tasks = TuModelo.objects.filter(user=request.user.id)
        serializer = TuModeloSerializer(tasks, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        data_with_pk = request.data.copy() 
        data_with_pk["user"] = request.user.id 
        serializer = TuModeloSerializer(data=data_with_pk)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
def add_imagen(request):
    if request.method == 'GET':
        tasks = Imagen.objects.all()
        serializer = ImagenSerializer(tasks, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ImagenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])  
def users_who_liked_task(request, task_id):
    try:
        task = Task.objects.prefetch_related('like_set').get(id=task_id)

        users = [like.user for like in task.like_set.all()]

        user_serializer = UserSerializer(users, many=True)

        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([AllowAny])  
def users_who_liked_task_comment(request, task_id):
    try:
        comment = Comment.objects.prefetch_related('likecomment_set').get(id=task_id)

        users = [like.user for like in comment.likecomment_set.all()]

        user_serializer = UserSerializer(users, many=True)

        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
def tasks_by_id(request, task_id):
    if request.method == 'GET':
        tasks = Task.objects.filter(id=task_id).prefetch_related('like_set')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
   
class NewPeticionCommentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, task_id):
        data = request.data.dict()
        data['post'] = task_id
        data['created_by'] = request.user.id

        print("Data to be serialized:", data)
        if 'aportacion' in request.data and request.data['aportacion']:
            data['aportacion'] = request.data['aportacion']
        
        serializer = CreateNewPeticionCommentSerializer(data=data)
        if serializer.is_valid():
            print("Datos validados y serializados:", serializer.validated_data)
            comment = serializer.save()

            index = 0
            while f'subtasks[{index}][title]' in request.data:
                subtask_data = {
                    'title': request.data.get(f'subtasks[{index}][title]'),
                    'description': request.data.get(f'subtasks[{index}][description]'),
                    'parent_task': comment.id,
                    'image': request.FILES.get(f'subtasks[{index}][image]'),
                    'video': request.FILES.get(f'subtasks[{index}][video]'),
                    'link': request.data.get(f'subtasks[{index}][link]')
                }
                print(f"Subtask {index} data to be serialized:", subtask_data)

                subtask_serializer = SubTaskCommentPostSerializer(data=subtask_data)
                if subtask_serializer.is_valid():
                    subtask_serializer.save()
                else:
                    print("Subtask serializer errors:", subtask_serializer.errors)
                    return Response(subtask_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                index += 1

            index = 0 
            while f'subfuentes[{index}][title]' in request.data:
                subFuentes_data = {
                    'title': request.data.get(f'subfuentes[{index}][title]'),
                    'description': request.data.get(f'subfuentes[{index}][description]'),
                    'parent_task': comment.id,
                    'image': request.FILES.get(f'subfuentes[{index}][image]'),
                    'video': request.FILES.get(f'subfuentes[{index}][video]'),
                    'link': request.data.get(f'subfuentes[{index}][link]')
                }
                print(f"Subfuentes {index} data to be serialized:", subFuentes_data)

                subfuentes_serializer = SubFuentesPCHPostSerializer(data=subFuentes_data)
                if subfuentes_serializer.is_valid():
                    subfuentes_serializer.save()
                else:
                    print("Subfuentes serializer errors:", subfuentes_serializer.errors)
                    return Response(subfuentes_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                index += 1

            index = 0 
            while f'subfactores[{index}][title]' in request.data:
                subFactores_data = {
                    'title': request.data.get(f'subfactores[{index}][title]'),
                    'description': request.data.get(f'subfactores[{index}][description]'),
                    'parent_task': comment.id,
                    'image': request.FILES.get(f'subfactores[{index}][image]'),
                    'video': request.FILES.get(f'subfactores[{index}][video]'),
                    'link': request.data.get(f'subfactores[{index}][link]')
                }
                print(f"Subfactores {index} data to be serialized:", subFactores_data)

                subfactores_serializer = SubFactoresPCHPostSerializer(data=subFactores_data)
                if subfactores_serializer.is_valid():
                    subfactores_serializer.save()
                else:
                    print("Subfactores serializer errors:", subfactores_serializer.errors)
                    return Response(subfactores_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                index += 1

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, task_id):
        comments = NewPeticionCommentPost.objects.filter(post=task_id).order_by('-created_at')
        serializer = NewPeticionCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NewPeticionCommentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, comment_id):
        return get_object_or_404(NewPeticionCommentPost, id=comment_id)

    def get(self, request, task_id, comment_id):
        comment_instance = self.get_object(comment_id)
        serializer = NewPeticionCommentSerializer(comment_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, task_id, comment_id):
        comment_instance = self.get_object(comment_id)
        data = request.data
        serializer = NewPeticionCommentSerializer(instance=comment_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id, comment_id):
        comment_instance = self.get_object(comment_id)
        comment_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)


class LikeCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id, comment_id):
        comment = get_object_or_404(NewPeticionCommentPost, id=comment_id)
        like = comment.likes.filter(user=request.user).first()
        if like:
            like.delete()
            liked = False
        else:
            LikeCommentPost.objects.create(user=request.user, comment=comment)
            liked = True
        return Response({'liked': liked, 'likes_count': comment.likes.count()}, status=200)
    
@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
def tasks_by_user(request, user_id):
    if request.method == 'GET':
        tasks = Task.objects.filter(user_id=user_id).prefetch_related('like_set')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def comment_detail(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        like = comment.likecomment_set.filter(user=request.user).first()
        
        if like:
            like.delete()
            return Response({'status': 'like removed'}, status=status.HTTP_200_OK)

        else:
            serializer = LikeCommentSerializer(data={'comment': comment_id})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.user == request.user:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this comment."}, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'DELETE':
        task = get_object_or_404(Comment, id=comment_id)
        task.delete()
        return Response(status=204)
    

@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser,MultiPartParser, FormParser])
def task_detaill(request, task_id):

    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user.id).prefetch_related('like_set')
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        print("Received data:", request.data)
        print("Received files:", request.FILES)
        task_data = {
            'title': request.data.get('title'),
            'description': request.data.get('description'),
            'username': request.data.get('username'),
            'pch': request.data.get('pch'),
            'categories': request.data.get('categories'),
            'user': request.user.id,
            'image': request.FILES.get('image'),
            'video': request.FILES.get('video'),
        }
        task_serializer = TaskSerializer(data=task_data)
        if task_serializer.is_valid():
            task = task_serializer.save()

            index = 0
            while f'subtasks[{index}][title]' in request.data:
                subtask_data = {
                    'title': request.data.get(f'subtasks[{index}][title]'),
                    'description': request.data.get(f'subtasks[{index}][description]'),
                    'parent_task': task.id,
                    'image': request.FILES.get(f'subtasks[{index}][image]'),
                    'video': request.FILES.get(f'subtasks[{index}][video]'),
                    'link': request.data.get(f'subtasks[{index}][link]'),
                }
                print(f"Processing subtask {index}: ", subtask_data) 
                subtask_serializer = SubTaskSerializer(data=subtask_data)
                print("Subtask serializer data:", subtask_serializer.initial_data) 
                if subtask_serializer.is_valid():
                    subtask_serializer.save()
                else:
                    print("Subtask serializer errors:", subtask_serializer.errors)  
                    return Response(subtask_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                index += 1

            
            index = 0  
            while f'subfuentes[{index}][title]' in request.data:
                subFuentes_data = {
                    'title': request.data.get(f'subfuentes[{index}][title]'),
                    'description': request.data.get(f'subfuentes[{index}][description]'),
                    'parent_task': task.id,
                    'image': request.FILES.get(f'subfuentes[{index}][image]'),
                    'video': request.FILES.get(f'subfuentes[{index}][video]'),
                    'link': request.data.get(f'subfuentes[{index}][link]')
                }
                print(f"Subfuentes {index} data to be serialized:", subFuentes_data)

                subfuentes_serializer = SubFuentesSerializer(data=subFuentes_data)
                if subfuentes_serializer.is_valid():
                    subfuentes_serializer.save()
                else:
                    print("Subfuentes serializer errors:", subfuentes_serializer.errors)
                    return Response(subfuentes_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                index += 1

            index = 0  
            while f'subfactores[{index}][title]' in request.data:
                subFactores_data = {
                    'title': request.data.get(f'subfactores[{index}][title]'),
                    'description': request.data.get(f'subfactores[{index}][description]'),
                    'parent_task': task.id,
                    'image': request.FILES.get(f'subfactores[{index}][image]'),
                    'video': request.FILES.get(f'subfactores[{index}][video]'),
                    'link': request.data.get(f'subfactores[{index}][link]')
                }
                print(f"Subfactores {index} data to be serialized:", subFactores_data)

                subfactores_serializer = SubFactoresSerializer(data=subFactores_data)
                if subfactores_serializer.is_valid():
                    subfactores_serializer.save()
                else:
                    print("Subfactores serializer errors:", subfactores_serializer.errors)
                    return Response(subfactores_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                index += 1

            return Response(task_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'PUT':
        try:
            task = Task.objects.get(id=task_id) 
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)  

        like = task.like_set.filter(user=request.user).first()
        
        if like:
            like.delete()
            return Response({'status': 'like removed'}, status=status.HTTP_200_OK)

        else:
            serializer = LikeSerializer(data={'task': task_id})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task = get_object_or_404(Task, id=task_id, user_id=request.user.id)
        task.delete()
        return Response(status=204)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_task_by_id(request, task_id):
    try:
        task = Task.objects.get(id=task_id)  
        serializer = TaskSerializer(task)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
def nuevo_task_detaill(request, task_id):
    if request.method == 'GET':
        try:
            task = Task.objects.get(id=task_id) 
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task) 
        return Response(serializer.data)

    elif request.method == 'POST':
        data_with_pk = request.data.copy() 
        data_with_pk["user"] = request.user.id  
        serializer = NuevoTaskSerializer(data=data_with_pk)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    try:
        task = NuevoTask.objects.get(id=task_id)
    except NuevoTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        like = task.like_set.filter(user=request.user).first()
        
        if like:
            like.delete()
            return Response({'status': 'like removed'}, status=status.HTTP_200_OK)

        else:
            serializer = LikeSerializer(data={'task': task_id})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task = get_object_or_404(NuevoTask, id=task_id, user_id=request.user.id)
        task.delete()
        return Response(status=204)

@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
def nuevo_task_detail(request):
    if request.method == 'GET':
        tasks = NuevoTask.objects.all()
        serializer = NuevoTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    return JsonResponse({'status': 'received'})

@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes([AllowAny])
def task_detail(request):
    if request.method == 'GET':
        
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        print(request.data)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=400)
    
@api_view(['POST'])
def test_view(request):
    print(request.data)
    categories_json = request.data.get('categories', '[]')
    print("Categories JSON:", categories_json)
    return Response({'status': 'Received'})
# auth start

@api_view(["POST",])
@permission_classes([AllowAny])
def SignUpView(request):
    if request.method == "POST":
        serializer = SignUpSerializer(data=request.data['user'])
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            profile = request.data['profile']
            user.profile.middle_name = profile['middle_name']
            user.profile.phone_number = profile['phone_number']
            user.save()
            token = Token.objects.get(user=user)
            user = UserSerializer(user)
            data['response'] = "successfully registered a new user."
            data['signedIn'] = True
            data['token'] = token.key
            data['user'] = user.data
        else:
            data['errors'] = serializer.errors
            data['signedIn'] = False
        return Response(data)

@api_view(["POST",])
@permission_classes([AllowAny])
def ValidateAccountView(request):
    if request.method == "POST":
        serializer = SignUpSerializer(data=request.data['account'], context={'type': 'account'})
        try:
            serializer.is_valid(raise_exception=True)
            return Response(status=204)
        except:
            if serializer.errors:
                return Response(data=serializer.errors, status=422)


@api_view(["POST",])
@permission_classes([AllowAny])
def ForgotPasswordView(request):
    send_forgot_password_email(request.data['email'])
    return Response()


@api_view(["POST",])
@permission_classes([AllowAny])
def ResetPasswordView(request):
    status = reset_password(token=request.data['token'], password=request.data['password'])
    return Response(status)
# auth end


@api_view(["GET"])
def GetUserView(request):
    if request.method == "GET":
        user = UserSerializer(request.user)
        subscriptionStatus = get_subscription(request.user)
        data = {
            'message': 'get request recieved from getuserview',
            'user': user.data,
            'subscriptionStatus': subscriptionStatus
        }

        return Response(data) 

@api_view(["PUT"])
def EditUserView(request):
    user = User.objects.get(pk=request.user.id)
    if request.data['first_name'] != None:    
        user.first_name = request.data["first_name"]
    if request.data['last_name'] != None:
        user.last_name = request.data["last_name"]
    if request.data['username'] != None:
        user.username = request.data["username"]
    if request.data['phone_number'] != None:
        user.profile.phone_number = request.data["phone_number"]
    if request.data['email'] != None:
        user.email = request.data["email"]

    user.save()

    return Response({ 'user': UserSerializer(user).data })

@api_view(["POST",])
# @permission_classes([AllowAny])
def ProfileImageView(request):
    user = request.user

    try:
        image_data = request.data['image']
        format, image_data = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_name = "profile_image"
        profile_image = ContentFile(base64.b64decode(image_data), name=image_name + ext)

        profile_image = ProfileImage.objects.create(
            file = profile_image
        )
        img_url = profile_image.file.url
       
        user.profile.image = img_url
        user.save()
        return Response({"success"},status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"Errors"}, status=status.HTTP_400_BAD_REQUEST)



class PostsView(APIView, PageNumberPagination):
    page_size = 10
    max_page_size = 1000

    def get_queryset(self):
        posts = Post.objects.all().order_by('-submittedOn')
        return self.paginate_queryset(posts, self.request)
    
    def get(self, request):
        posts = self.get_queryset()
        serializer = PostSerializer(posts, many=True)
        return self.get_paginated_response(serializer.data)


##### ADMIN VIEWS #####

class AdminUsersView(APIView, PageNumberPagination):
    page_size = 10
    max_page_size = 1000

    def get_queryset(self, params):
        if params:
            users = User.objects.filter( Q(username__contains=params['search']) | 
            Q(email__contains=params['search']) | Q(first_name__contains=params['search']) | Q(last_name__contains=params['search']) ).order_by('id')
        else:
            users = User.objects.all().order_by('id')
        return self.paginate_queryset(users, self.request)

    def get(self, request):
        params = request.query_params
        users = self.get_queryset(params)
        serializer = UserSerializer(users, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        json_data = json.loads(request.body)
        if json_data['post_type'] == 'CREATE': 
            try:
                user = User.objects.create_user(
                    username = json_data['username'],
                    first_name = json_data['first_name'],
                    last_name = json_data['last_name'],
                    email = json_data['email'],
                    password = json_data['password']
                )
                user.profile.role = json_data['role']
                user.profile.middle_name = json_data['middle_name']
                user.save()
                return Response({'Success': 'User Successfully Created'})
            except:
                return Response({'Error': 'Something Went Wrong'})
        elif json_data['post_type'] == 'EDIT':
            user = User.objects.get(id=json_data['id'])
            if user.username != json_data['username']:
                user.username = json_data['username']
            if user.first_name != json_data['first_name']:
                user.first_name = json_data['first_name']
            if user.last_name != json_data['last_name']:
                user.last_name == json_data['last_name']
            if user.profile.middle_name != json_data['middle_name']:
                user.profile.middle_name = json_data['middle_name']
            if user.email != json_data['email']:
                user.email = json_data['email']
            if json_data['role'] == "User":
                user.profile.role = 1
            if json_data['role'] == "Editor":
                user.profile.role = 2
            if json_data['role'] == "Admin":
                user.profile.role = 3
            try:
                user.save()
                return Response({"Success": "User Edit Successful"})
            except Exception as e:
                return Response({"Error": "Username Taken"})
        elif json_data['post_type'] == 'DELETE':
            User.objects.get(id=json_data['id']).delete()
            return Response({"Success": "User Deleted"})
        else:
            return Response({"Error": "Post Type Not Valid"})

class AdminPetitionEntriesView(APIView, PageNumberPagination):
    page_size = 10
    max_page_size = 1000

    def get_queryset(self, params):
        if params:
            petitionEntries = PetitionEntry.objects.filter( Q(name__contains=params['search']) | Q(phone_number__contains=params['search'])).order_by('id')
        else:
            petitionEntries = PetitionEntry.objects.all()
        return self.paginate_queryset(petitionEntries, self.request)

    def get(self, request):
        params = request.query_params
        petitionEntries = self.get_queryset(params)
        serializer = PetitionEntryGETSerializer(petitionEntries, many=True)
        return self.get_paginated_response(serializer.data)

class AdminPageView(APIView):

    def get(self, request):
        content = {
            "message":"Welcome "+ request.user.username,
            "users": UserSerializer(User.objects.all(), many=True).data
            }
        return Response(content)
    
    def post(self, request):
        json_data = json.loads(request.body)
        user = User.objects.get(id=json_data['id'])
        if user.profile.status == 1:
            user.profile.status = 2
        elif user.profile.status == 2:
            user.profile.status = 1
        else:
            user.profile.status = 3
        user.save()
        response = {
            'message': 'Switched user status',
            'user-status': user.profile.status
            }
        return Response(response)

class DashboardView(APIView):
    def get(self, request):
        user = UserSerializer(request.user)
        registration = RegistrationSerializer(Registration.objects.filter(user=request.user, payment_complete=True), many=True)
        content = {
            'registration': registration.data
        }
        return Response(content)

class UserListView(APIView):

    def get(self, request):
        users = UserSerializer(User.objects.all(), many=True)
        registrations = RegistrationSerializer(Registration.objects.filter(payment_complete=True), many=True)
        petitionEntries = PetitionEntryGETSerializer(PetitionEntry.objects.all(), many=True)
        agreements = AgreementSubmissionSerializer(AgreementSubmission.objects.all(), many=True)
        content = {
            "message": "User List",
            "users": users.data,
            "registrations": registrations.data,
            "petition_entries": petitionEntries.data,
            "agreementSubmissions": agreements.data,
        }
        return Response(content)


class PublicBlogView(APIView, PageNumberPagination):
    permission_classes = [AllowAny]
    page_size = 12

    def get_queryset(self):
        queryset = Blog.objects.filter(security=2, status=2).order_by('-created')
        return self.paginate_queryset(queryset, self.request)

    def get(self, request):
        posts = BlogSerializer(self.get_queryset(), many=True)
        res = {
            'Message':'Blog Get Request Recieved',
            'posts': posts.data,
        }
        return self.get_paginated_response(res)

class BlogView(APIView, PageNumberPagination):
    page_size = 12

    def get_queryset(self, params):
        try:
            queryset = Blog.objects.filter( title__contains=params['search'] ).order_by('-created')
        except:
            queryset = Blog.objects.all().order_by('-created')
        hidden = queryset.filter(~Q(createdBy=self.request.user), status=3)
        queryset = queryset.exclude(id__in=hidden)
        private = self.request.query_params.get('private', None)
        if private is not None:
            queryset = queryset.filter(status=2)
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__contains=title)
        return self.paginate_queryset(queryset, self.request)

    def get(self, request):
        params = request.query_params
        posts = BlogSerializer(self.get_queryset(params), many=True)
        res = {
            'Message':'Blog Get Request Recieved',
            'posts': posts.data,
        }
        return self.get_paginated_response(res)

    def post(self, request):
        if request.data['thumb_nail'] != '':
            image_data = request.data['thumb_nail']
            format, image_data = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_name = request.data['title'] + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            thumb_nail = ContentFile(base64.b64decode(image_data), name=image_name + ".jpeg")

            thumb_nail = Thumbnail.objects.create(
                file = thumb_nail
            )

            img_url = thumb_nail.file.url
        else:
            img_url = ""

        data = {
            'createdBy': request.user.id,
            'lastUpdatedBy': request.user.id,
            'title': request.data['title'],
            'summary': request.data['summary'],
            'thumb_nail': img_url,
            'content': request.data['content'],
            'status': int(request.data['status']),
            'security': int(request.data['security'])
        }
        post = BlogPOSTSerializer(data=data)
        if post.is_valid():
            post.save()
            res = {
                "message": "post created successfully",
                "post": post.data
            }
        else:
            res = {
                "message": "post creation unsuccessfully",
                "Errors": post.errors
            }
        return Response(res)
    
    def put(self, request):
        post = Blog.objects.get(id=request.data['id'])

        if request.data['thumb_nail'][0:6] == 'https:' or request.data['thumb_nail'] == '':
            img_url = post.thumb_nail
        else:
            image_data = request.data['thumb_nail']
            format, image_data = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_name = request.data['title'] + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            thumb_nail = ContentFile(base64.b64decode(image_data), name=image_name + ".jpeg")

            thumb_nail = Thumbnail.objects.create(
                file = thumb_nail
            )

            img_url = thumb_nail.file.url

        status = request.data['status']
        if status == "Draft":
            status = 1
        elif status == "Published":
            status = 2
        elif status == "Hidden":
            status = 3

        security = request.data['security']
        if security == "Private":
            security = 1
        elif security == "Public":
            security = 2
        
        data = {
            'createdBy': post.createdBy.id,
            'lastUpdatedBy': request.user.id,
            'title': request.data['title'],
            'summary': request.data['summary'],
            'thumb_nail': img_url,
            'content': request.data['content'],
            'status': status,
            'security': security
        }
        post = BlogPOSTSerializer(post, data=data)
        if post.is_valid():
            post.save()
            res = {
                "message": "post created successfully",
                "post": post.data
            }
        else:
            res = {
                "message": "post creation unsuccessfully",
                "Errors": post.errors
            }
        return Response(res)
        
    def delete(self, request):
        try:
            Blog.objects.get(id=request.data['id']).delete()
            res = {
                "status": "Success"
            }
        except:
            res = {
                "status": "Failed"
            }
        return Response(res)

class BlogDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        post = BlogSerializer(Blog.objects.get(id=slug))
        return Response(post.data)

        
class PetitionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        letters = string.ascii_lowercase
        image_data = request.data['signature']
        format, image_data = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_name = ''.join(random.choice(letters) for i in range(10))
        signature = ContentFile(base64.b64decode(image_data), name=image_name + ".jpeg")

        upload = Upload.objects.create(
            file = signature
        )
        img_url = upload.file.url

        data = {
            'petition': request.data['petition'],
            'name': request.data['name'],
            'phone_number': request.data['phone_number'],
            'signature': img_url
        }
        petition = PetitionEntrySerializer(data=data)
        if petition.is_valid():
            petition.save()
            res = {
                'message': "Successful Submission",
                'petition': petition.data
            }
        else:
            res = {
                'message': 'Error',
                "Error": petition.errors
            }
        return Response(res)

class RepresentativeSurveyEntryView(APIView):
    
    def get(self, request):
        existingSurvey = RepresentativeSurveyEntry.objects.filter(user=request.user)
        
        if existingSurvey.exists():
            return Response( data={'existingEntry': True} )
        else:
            return Response( data={'existingEntry': False} )

    def post(self, request):
        data = {
            'user' : request.user,
            **request.data
        }

        surveyEntry = RepresentativeSurveyEntry(**data)
        surveyEntry.save()

        return Response( data={'message': 'You created an entry, congrats!'} )

class CredencialSurveyEntryView(APIView):
    
    def get(self, request):
        existingSurvey = CredencialSurveyEntry.objects.filter(user=request.user)
        
        if existingSurvey.exists():
            return Response( data={'existingEntry': True} )
        else:
            return Response( data={'existingEntry': False} )

    def post(self, request):
        data = {
            'user' : request.user,
            **request.data
        }

        surveyEntry = CredencialSurveyEntry(**data)
        surveyEntry.save()

        return Response( data={'message': 'You created an entry, congrats!'} )

class VotingForAmmonSurveyEntryView(APIView):
    
    def get(self, request):
        existingSurvey = VotingForAmmonSurveyEntry.objects.filter(user=request.user)
        
        if existingSurvey.exists():
            return Response( data={'existingEntry': True} )
        else:
            return Response( data={'existingEntry': False} )

    def post(self, request):
        data = {
            'user' : request.user,
            **request.data
        }

        surveyEntry = VotingForAmmonSurveyEntry(**data)
        surveyEntry.save()

        return Response( data={'message': 'You created an entry, congrats!'} )


class AgreementView(APIView):
    def get(self, request):
        agreements = AgreementSubmission.objects.filter(user=request.user)
        if agreements:
            res = {
                "Agreement": "Submitted"
            }
        else:
            res = {
                "Agreement": "Pending"
            }
        return Response(res)

    def post(self, request):
        agreement = AgreementSubmission.objects.create(
            user = request.user,
            agreement = "Agreement #1"
        )
        res = {
            'Success': 'Success'
        }
        return Response(res)


@api_view(["GET"])
@permission_classes([AllowAny])
def LandingPageView(request):
    
    three_newest_blogs = Blog.objects.filter(status=2, security=2).order_by('-created')[:3]
    
    data = { "blogs" : [] }

    for blog in three_newest_blogs:
        
        data["blogs"].append({
            'id': blog.id,
            'title' : blog.title,
            'summary' : blog.summary
        })
    
    
    return Response(data)


class CurrencyView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        currencyObject = Currency.objects.all().order_by('name')
        try:
            currencies = CurrencySerializer(currencyObject, many=True).data
        except:
            currencies = None
       
        res = {
            "base": "USD",
            "data": datetime.now().strftime("%Y-%m-%d"),
            "rates":currencies
        }

        return Response(res)

class AdminCurrencyView(APIView):
    def put(self, request):
        currency = Currency.objects.get(id=request.data['id'])
        if request.data['name'] != None:
            currency.name = request.data['name']
        if request.data['sell'] != None:
            currency.sell = request.data['sell']
        if request.data['buy'] != None:
            currency.buy = request.data['buy']
        currency.save()
        res = {
            'status':"Success"
        }
        return Response(res)

class DirectoryView(APIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Directory.objects.all().order_by('name')
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        return queryset
    
    def get(self, request):
        directoryObj = self.get_queryset()
        try:
            directory = DirectorySerializer(directoryObj, many=True).data
        except:
            directory = None
       
        res = {
            "data":directory
        }

        return Response(res)

class AdminDirectoryView(APIView):
    def delete(self, request):
        Directory.objects.get(id=request.data['id']).delete()
        res = {
            'status': 'Success'
        }
        return Response(res)

    def put(self, request):
        directory = Directory.objects.get(id=request.data['id'])
        if directory.businessPage:
            BP = BusinessPage.objects.get(id=directory.businessPage.id)
        else:
            BP = None
        if request.data["name"] != None:
            directory.name = request.data['name']
        if request.data["latitude"] != None:
            directory.latitude = request.data['latitude']
        if request.data["longitude"] != None:
            directory.longitude = request.data['longitude']
        if request.data["phone_number"] != None:
            directory.phone_number = request.data['phone_number']
        if request.data["category"] != None:
            directory.category = request.data['category']
        if request.data["status"] != None:
            BP.status = request.data['status']
            BP.save()
        directory.save()
        res = {
            'status':"Success",
            'directory': DirectorySerializer(directory).data
        }
        return Response(res)

    def post(self, request):
        directoryObj = DirectorySerializer(data=request.data)
        if directoryObj.is_valid():
            directoryObj.save()
            res = {
            'status':"Success",
            'directory': directoryObj.data
            }
        else:
            res = {
                'status':"Fail",
                "errors": directoryObj.errors
            }
        return Response(res)
    
class BusinessPageAdminView(APIView):
    def post(self, request):
        directoryItem = Directory.objects.get(id=request.data['directoryItem'])
        businessPage = BusinessPage.objects.create(
            name = directoryItem.name,
            phone_number = directoryItem.phone_number,
            latitude = directoryItem.latitude,
            longitude = directoryItem.longitude,
        )
        directoryItem.businessPage = businessPage
        directoryItem.save()
        res = {
            'status': 'Success',
            'pageId': businessPage.id
        }
        return Response(res)
    
    def put(self, request):
        if request.data['type'] == "Map":
            page = BusinessPage.objects.get(id=request.data['page'])
            latitude = request.data['latitude']
            longitude = request.data['longitude']
            page.latitude = latitude
            page.longitude = longitude
            page.save()
            res = {'status': 'Success'}
        if request.data['type'] == "Images":
            page = BusinessPage.objects.get(id=request.data['page'])
            img_count = 0
            
            for obj in request.data["images"]:
                img_count += 1
                image_data = obj['data']
                format, image_data = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_name = "${}-${}".format(page.name, img_count)
                raw_image = ContentFile(base64.b64decode(image_data), name=image_name + ".jpeg")
                image = BusinessPagePhoto.objects.create(
                    file = raw_image
                )
                page.photos.add(image)
            res = {'status': 'Success'}
        if request.data['type'] == "Banner":
            page = BusinessPage.objects.get(id=request.data['page'])
            for obj in request.data['image']:
                image_data = obj['data']
                format, image_data = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_name = "${}-banner".format(page.name)
                raw_image = ContentFile(base64.b64decode(image_data), name=image_name + ".jpeg")
                image = BusinessPagePhoto.objects.create(
                    file = raw_image
                )
                try:
                    page.banner.delete()
                except: 
                    pass
                page.banner = image
                page.save()
            res = {'status': 'Success'}
        if request.data['type'] == "Info":
            data = request.data
            data.pop('type')
            BusinessPage.objects.filter(id=request.data['id']).update(**data)
            res = {
                'status': 'Success'
            }
        return Response(res)


class BusinessPageView(APIView):
    def get(self, request, slug):
        businessPage = BusinessPage.objects.get(id=slug)
        page = BusinessPageSerializer(businessPage)
        posts = BusinessPagePostSerializer(BusinessPagePost.objects.filter(page=businessPage).order_by('-created_at'), many=True)
        res = {
            "status":"Success",
            "page": page.data,
            "posts": posts.data
        }
        return Response(res)      
    
    def post(self, request):
        res = {
            'status': 'Success'
        }
        return Response(res)

class BusinessPostDetailsView(APIView):
    def get(self, request, slug):
        post = BusinessPagePostSerializer(BusinessPagePost.objects.get(id=slug))
        res = {
            "status":"Success",
            "post": post.data
        }
        return Response(res)   


class CreateCheckoutSession(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        try:
            customer = StripeCustomer.objects.get(user=data['userId'])
            cancel_url = "http://localhost:3000/dashboard/subscription"
            success_url = "http://localhost:3000/dashboard/subscription/success"
            subscription_data = {}
        except:
            customer = None
            cancel_url = "http://localhost:3000/registration/subscription/{}".format(data['userId'])
            success_url="http://localhost:3000/registration/subscriptionSuccess"
            subscription_data = {'trial_period_days': 30}

        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id="{}_registration".format(data['userId']),
                customer=customer,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_method_types=["card"],
                mode="subscription",
                line_items=[
                    {
                        "price": data['priceId'],
                        "quantity": 1
                    }
                ],
                subscription_data=subscription_data,
            )
            return Response({'sessionId': checkout_session['id']})
        except Exception as e:
            print(e)
            return Response({'error': {'message': str(e)}}, 400)


class SubscriptionView(APIView):
    def delete(self, request):
        user = request.user

        customer = StripeCustomer.objects.get(user=user)
        stripe.Subscription.delete(customer.stripeSubscriptionId)
        customer.stripeSubscriptionId = None
        customer.save()

        user.profile.subscriptionActive = False
        user.save()

        return Response({ 'subscription': get_subscription(user) })

class UserCalendarEventView(APIView):
    def get(self, request):
        events = CalendarEvent.objects.filter(
            Q(category__isnull=True) | Q(category__in=request.user.profile.calendar_event_categories.all())
        )
        eventsSerializer = CalendarEventSerializer(events, many=True)

        categories = CalendarEventCategory.objects.all()
        categoriesSerializer = CalendarEventCategorySerializer(categories, many=True)

        return Response({ 'events': eventsSerializer.data, 'categories': categoriesSerializer.data })

class UserCalendarEventCategoryView(APIView):
    def patch(self, request):
        categories = request.data['categories']
        request.user.profile.calendar_event_categories.set(categories, clear=True)

        events = CalendarEvent.objects.filter(
            Q(category__isnull=True) | Q(category__in=request.user.profile.calendar_event_categories.all())
        )
        eventsSerializer = CalendarEventSerializer(events, many=True)

        return Response({ 'events': eventsSerializer.data })

@permission_classes([isEditorOrAdminPermission])
class CalendarEventCategoryView(APIView):
    def post(self, request):
        data = request.data['category']
        CalendarEventCategory.objects.create(**data)
        return Response({ 'categories': self.get_all_categories() })

    def patch(self, request, pk):
        categoryData = request.data['category']
        CalendarEventCategory.objects.filter(pk=pk).update(**categoryData)
        return Response({ 'categories': self.get_all_categories() })

    def delete(self, request, pk):
        CalendarEventCategory.objects.filter(pk=pk).delete()
        return Response({ 'categories': self.get_all_categories() })

    def get_all_categories(self):
        categories = CalendarEventCategory.objects.all()
        return CalendarEventCategorySerializer(categories, many=True).data


@permission_classes([isEditorOrAdminPermission])
class AdminCalendarEventView(APIView):
    def get(self, request):
        return Response({ 'events': self.get_all_events(request.user), 'categories': self.get_all_categories() })

    def post(self, request):
        data = request.data['event']
        CalendarEvent.objects.create(**data)
        return Response({ 'events': self.get_all_events(request.user) })

    def patch(self, request, pk):
        eventData = request.data['event']
        event = CalendarEvent.objects.filter(pk=pk)
        event.update(**eventData)
        return Response({ 'events': self.get_all_events(request.user) })

    def delete(self, request, pk):
        CalendarEvent.objects.filter(pk=pk).delete()
        return Response({ 'events': self.get_all_events(request.user) })

    def get_all_categories(self):
        categories = CalendarEventCategory.objects.all()
        return CalendarEventCategorySerializer(categories, many=True).data

    def get_all_events(self, user):
        events = CalendarEvent.objects.all()
        serializer = CalendarEventSerializer(events, many=True)
        return serializer.data


class CreateRaffleCheckoutSession(APIView):
    def post(self, request):
        data = request.data
        try:
            stripeCustomer = StripeCustomer.objects.get(user=request.user)
        except:
            stripeCustomer = None

        if stripeCustomer:
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id="{}_raffle-ticket".format(request.user.id),
                    customer = stripeCustomer.stripeCustomerId,
                    success_url="http://localhost:3000/dashboard/raffle/success",
                    cancel_url="http://localhost:3000/dashboard/raffle",
                    payment_method_types=["card"],
                    mode=data['mode'],
                    line_items=[
                        {
                            "price": data['priceId'],
                            "quantity": 1
                        }
                    ]
                )
                return Response({'sessionId': checkout_session['id']})
            except Exception as e:
                return Response({'error': {'message': str(e)}}), 400
        else:
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id="{}_raffle-ticket".format(request.user.id),
                    success_url="http://localhost:3000/dashboard/raffle/success",
                    cancel_url="http://localhost:3000/dashboard/raffle",
                    payment_method_types=["card"],
                    mode=data['mode'],
                    line_items=[
                        {
                            "price": data['priceId'],
                            "quantity": 1
                        }
                    ]
                )
                return Response({'sessionId': checkout_session['id']})
            except Exception as e:
                return Response({'error': {'message': str(e)}}), 400






class GroupView(APIView, PageNumberPagination):
    page_size = 10
    max_page_size = 1000

    def get_queryset(self, params):
        try:
            groups = Group.objects.filter(leader__first_name__contains=params['search']).order_by('id')
        except:
            groups = Group.objects.all().order_by('id')
        return self.paginate_queryset(groups, self.request)

    def get(self, request):
        params = request.query_params
        groups = self.get_queryset(params)
        serializer = GroupSerializer(groups, many=True)
        return self.get_paginated_response(serializer.data)
    
    def post(self, request):
        if request.data['post_type'] == 'join_group':
            group = Group.objects.get(id=request.data['groupId'])
            user = request.user
            if group.members.count() < 10:
                group.members.add(user)

                return Response({
                    'success': 'User added to group'
                })
            else:
                return Response({
                    'error': 'Group is full.'
                })

        elif request.data['post_type'] == 'create_group':
            try:
                group = Group.objects.create(
                    leader = request.user,
                    description = request.data['description']
                )
                group.members.add(request.user)

                return Response({
                    'success': "Group Created"
                })
            except Exception as e: 
                return Response({
                    'error': "Couldn't create group."
                })
        else:
            return Response({
                'error': 'Unknown Request'
            })


class MyGroupView(APIView):
    def get(self, request):
        group = Group.objects.get(members=request.user)
        if(group != None):
            groupMessages = GroupMessage.objects.filter(group=group).order_by('-id')
            return Response({
                "success": "User Has Group",
                "groupMessages": GroupMessageSerializer(groupMessages, many=True).data,
                "group": GroupSerializer(group).data
            })
        else:
            return Response({
                "error": "User Doesn't Have Group"
            })
    
    def post(self, request):
        if request.data['post_type'] == "removeUser":
            group = Group.objects.get(id=request.data['group'])
            user = User.objects.get(id=request.data['user'])
            if request.user != group.leader:
                return Response({
                    "error": 'Not authorized to add or remove users.'
                })
            else:
                group.members.remove(user)
                group.save()
                return Response({
                    "success": "User Removed From Group",
                    "group": GroupSerializer(group).data
                })
        elif request.data['post_type'] == "makeLeader":
            group = Group.objects.get(id=request.data['group'])
            user = User.objects.get(id=request.data['user'])
            if request.user != group.leader:
                return Response({
                    "error": 'Not authorized to add or remove users.'
                })
            else:
                group.leader = user
                group.save()
                return Response({
                    "success": "Leader has been changed",
                    "group": GroupSerializer(group).data
                })

        elif request.data['post_type'] == "addUser":
            group = Group.objects.get(id=request.data['group'])
            user = User.objects.get(id=request.data['user'])
            group.members.add(user)
            group.save()

            return Response({
                "success": "User has been added",
                "group": GroupSerializer(group).data
            })

        elif request.data['post_type'] == "leaveGroup":
            group = Group.objects.get(id=request.data['group'])
            user = request.user
            if group.leader == user:
                group.members.remove(user)
                if group.members.count() == 0:
                    group.delete()
                else:
                    group.leader = group.members.all()[0]
                    group.save()
            else:    
                group.members.remove(user)
                group.save()
            return Response({
                "success": "User has left group",
            })
        
        elif request.data['post_type'] == "editDesc":
            group = Group.objects.get(id=request.data['group'])
            user = request.user
            if group.leader == user:
                group.description = request.data['description']
                group.save()
                res = {"success": "desc edit succesful"}
            else:
                res = {"error": "User Not Leader"} 
            return Response(res)
        else:
            return Response({
                "error": 'unknown post_type'
            })
    

class GroupMessageView(APIView):
    def get(self, request, slug):
        group = Group.objects.get(id=slug)
        group_messages = GroupMessage.objects.filter(group=group)
        serializer = GroupMessageSerializer(group_messages, many=True)

        res = {
            "messages": serializer.data
        }
        return Response(res)     

    def post(self, request, slug):
        if request.data['post_type'] == 'delete':
            message = GroupMessage.objects.get(id=request.data['messageId']) 
            group = Group.objects.get(id=slug)
            if request.user == message.creator or request.user == group.leader:
                message.delete()
                groupMessages = GroupMessage.objects.filter(group=slug)
                return Response({
                    "success": "Message deleted.",
                    "groupMessages": GroupMessageSerializer(groupMessages, many=True).data
                })
            else:
                return Response({
                    "error": "User is not authorized to delete message."
                })
        else:
            messageData = request.data["messageData"]
            serializer = GroupCreateMessageSerializer(data=messageData)
            if serializer.is_valid():
                serializer.save()
                groupMessages = GroupMessage.objects.filter(group=slug)
                return Response({
                    "success": "Group Message successfully created",
                    "groupMessages": GroupMessageSerializer(groupMessages, many=True).data
                })
            else: 
                return Response({
                    "error": "Group message not created."
                })


class YOI_Homepage(APIView):
    def get(self, request):
        return Response({ "count": YOI_Registration.objects.filter(payment_complete=True).count() })

class CreateYOICheckoutSession(APIView):
    def post(self, request):
        try:
            children = request.data['children']

            saved_children = []
            for child in children:
                saved_child = YOI_Registration.objects.create(
                    first_name = child['first_name'],
                    last_name = child['last_name'],
                    birthdate = child['birthday'],
                    email = child['email'],
                    phone_number = child['phone_number'],
                    allergies = child['allergies'],
                    size = child['size'],
                    parent = request.user,
                    gender = int(child['gender']),
                    translation_assistance = child['translation_assistance'],
                    spanish_shirt = child['spanish_shirt'],
                )

                saved_children.append(str(saved_child.id))

            checkout_session = self.get_stripe_session(
                request.user,
                request.data['price'],
                request.data['quantity'],
                "http://localhost:3000/dashboard/YOI/register-success",
                "http://localhost:3000/dashboard/YOI/register",
                "{}_YOI_{}".format(request.user.id, ','.join(saved_children))
            )

            return Response({'sessionId': checkout_session['id']})
        except Exception as e:
            return Response({'error': {'message': str(e)}}, 400)

    def patch(self, request):
        try:
            checkout_session = self.get_stripe_session(
                request.user,
                request.data['price'],
                request.data['quantity'],
                "http://localhost:3000/dashboard/YOI/registrations?success",
                "http://localhost:3000/dashboard/YOI/registrations",
                "{}_YOI_{}".format(request.user.id, ','.join(map(str, request.data['children'])))
            )
            return Response({'sessionId': checkout_session['id']})
        except Exception as e:
            return Response({'error': {'message': str(e)}}, 400)

    def get_stripe_session(self, user, price, quantity, success_url, cancel_url, client_reference_id):
        try:
            customer = StripeCustomer.objects.get(user=user)
        except:
            customer = None

        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer = customer,
            client_reference_id=client_reference_id,
            mode='payment',
            line_items=[{
                'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'YOI Registration',
                },
                'unit_amount': int(price),
                },
                'quantity': int(quantity),
            }],
            success_url=success_url,
            cancel_url=cancel_url,
        )

class YOI_AssistantView(APIView):
    def post(self, request):
        data = request.data['data']
        data['user']=request.user.id
        form = YOI_AssistantSerializer(data=data)
        if form.is_valid():
            form.save()
            res = {
            'success':"Form successfully submited",
            }
        else:
            res = {
                "errors": form.errors
            }
        return Response(res)

class YOI_RegistrationView(APIView):
    def get(self, request):
        registrations = YOI_Registration.objects.filter(parent=request.user)
        serializer = YOI_RegistrationSerializer(registrations, many=True)
        return Response({
            "registrations": serializer.data
        })

    def patch(self, request, pk):
        kid = get_object_or_404(YOI_Registration, pk=pk)
        try:
            kid.email = request.data['email']
            kid.phone_number = request.data['phone_number']
            kid.allergies = request.data['allergies']
            kid.size = request.data['size']
            kid.save()
            registrations = YOI_Registration.objects.filter(parent=request.user)
            serializer = YOI_RegistrationSerializer(registrations, many=True)
            return Response({'registrations': serializer.data})
        except Exception as e:
            return Response({'error': {'message': str(e)}}, 400)

    def post(self, request):
        json_data = json.loads(request.body)
        json_data = json_data['data']
        parent, status = create_parent(json_data['parent'])
        if status == "Success":
            child, status = create_child(json_data['child'])
            if status == "Success":
                registration = create_registration(json_data['registration'], request.user, parent, child)
                if registration:
                    registration = RegistrationSerializer(registration).data
                    res = {
                        'message': 'Test Registration Complete',
                        'Registration': registration,
                        'status': 'Success',
                    }
                    return Response(res)
                else:
                    parent.delete()
                    child.delete()
                    res = {
                        'message': 'Error: Problem creating child',
                        'status': 'Error'
                    }
                    return Response(res)
            else:
                parent.delete()
                res = {
                    'message': 'Error: Problem creating child',
                    'status': 'Error'
                }
                return Response(res)
        else:
            res = {
                'message': 'Error: Problem creating parent.',
                'status': 'Error'
            }
            return Response(res)

class YOIAdminView(APIView):
    def get(self, request):
        registrations = YOI_Registration.objects.filter(payment_complete=True)
        registrations_serializer = YOI_RegistrationSerializer(registrations, many=True)

        assistants = YOI_Assistant.objects.order_by('-created').filter(created__year=datetime.now().date().year)
        assistants_serializer = YOI_AssistantSerializer(assistants, many=True)

        return Response({ 'children': registrations_serializer.data, 'assistants': assistants_serializer.data })



class StripeWebhooks(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        event = None

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            return Response(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            client_reference_id = session.get('client_reference_id').split("_")
            stripe_customer_id = session.get('customer')
            stripe_subscription_id = session.get('subscription')

            if client_reference_id[1] == 'raffle-ticket':
                user = User.objects.get(id=client_reference_id[0])
                if stripe_subscription_id:
                    RaffleEntry.objects.create(
                        user=user,
                        stripeCustomerId=stripe_customer_id,
                        stripeSubscriptionId=stripe_subscription_id,
                    )
                else:
                    RaffleEntry.objects.create(
                        user=user,
                        stripeCustomerId=stripe_customer_id,
                        stripePaymentIntent=session.get('payment_intent'),
                    )
            elif client_reference_id[1] == 'registration':
                user = User.objects.get(id=client_reference_id[0])
                user.profile.subscriptionActive = True
                user.save()

                customer = StripeCustomer.objects.filter(user=user).first()
                if customer:
                    if (customer.stripeSubscriptionId):
                        try:
                            stripe.Subscription.delete(customer.stripeSubscriptionId)
                        except:
                            # If a subscription was already cancelled (for example, due to lack of payment), the delete method will throw an error.
                            pass

                    customer.stripeSubscriptionId = stripe_subscription_id
                    customer.save()
                else:
                    StripeCustomer.objects.create(
                        user=user,
                        stripeCustomerId=stripe_customer_id,
                        stripeSubscriptionId=stripe_subscription_id,
                    )
            elif client_reference_id[1] == 'YOI':
                user = User.objects.get(id=client_reference_id[0])
                registrations = YOI_Registration.objects.filter(id__in=client_reference_id[2].split(','))

                for child in registrations:
                    child.payment_complete = True
                    child.save()
       
        elif event['type'] == "invoice.payment_succeeded":
            session = event['data']['object']
            customer = session.get('customer')
            subscription = session.get('subscription')
            
            try:
                RaffleTicket = RaffleEntry.objects.get(stripeCustomerId=customer, stripeSubscriptionId=subscription)
            except:
                RaffleTicket = None
   
            if RaffleTicket != None:
                RaffleTicket.payments += 1
                RaffleTicket.save()
                if RaffleTicket.payments >= 10:
                    stripe.Subscription.delete(subscription)
        return Response(status=200)


class MyListingsView(APIView):
    def get(self, request):
        itemsQueryset = Listing.objects.filter(user=request.user).order_by('-id')
        vehiclesQueryset = VehicleListing.objects.filter(user=request.user).order_by('-id')
        listingId = self.request.query_params.get("listingId", None)
        search = self.request.query_params.get("search", None)

        if listingId:
            itemsQueryset = itemsQueryset.filter(id=listingId)
            vehiclesQueryset = vehiclesQueryset.filter(id=listingId)
        if search:
            itemsQueryset = itemsQueryset.filter(title__contains=search)
            vehiclesQueryset = vehiclesQueryset.filter(title__contains=search)
        
        itemsQueryset = ListingSerializer(itemsQueryset, many=True)
        vehiclesQueryset = VehicleListingSerializer(vehiclesQueryset, many=True)

        return Response({
            "items": itemsQueryset.data,
            "vehicles": vehiclesQueryset.data,
        })

    def put(self, request):
        type = request.data['type']
        if type == 'vehicle':
            listing = VehicleListing.objects.get(id=request.data['listingId'])
        elif type == 'classified':
            listing = Listing.objects.get(id=request.data['listingId'])
        if request.user != listing.user:
            return Response({
                "error": "Not The Owner Of This Listing"
            })
        listingData = request.data['listingData']
        listingData['expire_date'] = datetime.now() + timedelta(days=183)
        if type == 'vehicle':
            serializer = VehicleListingSerializer(listing, data={**listingData}, partial=True)
        elif type == 'classified':
            serializer = ListingSerializer(listing, data={**listingData}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": "Listing Updated",
                "response":  serializer.data
            })
        else:
            return Response({
                "error": "Listing Not Updated"
            })

class ListingsView(APIView, PageNumberPagination):
    page_size = 24
    max_page_size = 1000

    def get_queryset(self):
        queryset = Listing.objects.filter(available=True).order_by('-id')
        itemId = self.request.query_params.get("itemId", None)
        categories = self.request.query_params.get("categories", None)
        search = self.request.query_params.get("search", None)

        if search:
            queryset = queryset.filter(title__contains=search)
        elif itemId:
            queryset = queryset.filter(id=itemId)
        elif categories:
            categories = [int(x) for x in categories.split(',')]
            queryset = queryset.filter(category__in=categories)
        else:
            now = datetime.now()
            queryset = queryset.filter(expire_date__gt=now)
        return self.paginate_queryset(queryset, self.request)
    
    def get(self, request):
        objs = self.get_queryset()
        serializer = ListingSerializer(objs, many=True)
        return self.get_paginated_response(serializer.data)
    
    def post(self, request):
        listingData = request.data['listingData']
        listingData['user'] = (request.user.id)
        listingData['expire_date'] = datetime.now() + timedelta(days=183)
        listingObj = ListingSerializer(data=listingData)
        if listingObj.is_valid():
            listingObj.save()
            return Response({
                "success": "Listing Created",
                "listing": listingObj.data
            })
        else:
            return Response({
                    "error": "Listing Not Created"
                })
    
    def put(self, request):
        listing = Listing.objects.get(id=request.data['listing'])
        if request.user != listing.user:
            return Response({
                "error": "Not The Owner Of This Listing"
            })
        listingData = request.data['listingData']
        serializer = ListingSerializer(listing, data={**listingData}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": "Listing Updated",
                "listing":  serializer.data
            })
        else:
            return Response({
                "error": "Listing Not Updated"
            })
    
    def delete(self, request):
        try:
            listing = Listing.objects.get(id=request.data['listing'])
            if request.user == listing.user:
                listing.delete()
                return Response({
                    "success": "Listing Deleted",
                })
            else:
                return Response({
                    "error": "Not The Owner Of This Listing"
                })
        except:
            return Response({
                "error": "Listing Not Found"
            })

class VehicleListingsView(APIView, PageNumberPagination):
    page_size = 24
    max_page_size = 1000

    def get_queryset(self):
        queryset = VehicleListing.objects.filter(available=True).order_by('-id')
        vehicleId = self.request.query_params.get("vehicleId", None)
        search = self.request.query_params.get("search", None)
        
        if vehicleId:
            queryset = queryset.filter(id=vehicleId)
        elif search:
            queryset = queryset.filter(title__contains=search)
        else:
            now = datetime.now()
            queryset = queryset.filter(expire_date__gt=now)
        return self.paginate_queryset(queryset, self.request)

    def get(self, request):
        objs = self.get_queryset()
        serializer = VehicleListingSerializer(objs, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        listingData = request.data['listingData']
        listingData['user'] = (request.user.id)
        listingData['expire_date'] = datetime.now() + timedelta(days=183)
        listingObj = VehicleListingSerializer(data=listingData)
        if listingObj.is_valid():
            listingObj.save()
            return Response({
                "success": "Listing Created",
                "listing": listingObj.data
            })
        else:
            return Response({
                "error": "Listing Not Created"
            })
    
    def put(self, request):
        listing = VehicleListing.objects.get(id=request.data['listing'])
        if request.user != listing.user:
            return Response({
                "error": "Not The Owner Of This Listing"
            })
        listingData = request.data['listingData']
        serializer = VehicleListingSerializer(listing, data={**listingData}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": "Listing Updated",
                "listing":  serializer.data
            })
        else:
            return Response({
                "error": "Listing Not Updated"
            })

    def delete(self, request):
        try:
            listing = VehicleListing.objects.get(id=request.data['listing'])
            if request.user == listing.user:
                listing.delete()
                return Response({
                    "success": "Listing Deleted",
                })
            else:
                return Response({
                    "error": "Not The Owner Of This Listing"
                })
        except:
            return Response({
                "error": "Listing Not Found"
            })


class ListingImageUpload(APIView):

    def post(self, request):
        images = request.data['images']
        listingId = request.data['listingId']
        listingType = request.data['type']
        if listingType == "classified":
            listing = Listing.objects.get(id=listingId)
        else:
            listing = VehicleListing.objects.get(id=listingId)

        listing.available = False
        listing.save()

        for image in images:
            image_data = image["data"]
            image_name = image["name"].split(".")[0] + "_{}_listing_image".format(request.user.username)
            format, image_data = image_data.split(';base64,')
            imageFile = ContentFile(base64.b64decode(image_data), name=image_name + ".jpeg")

            listing_image = ListingImage.objects.create(
                file = imageFile
            )

            listing.photos.add(listing_image)
            listing.save()

        listing.available = True
        listing.save()
 
        return Response({
            "success": "images saved"
        })

    def delete(self, request):
        imageId = request.data['imageId']
        ListingImage.objects.get(id=imageId).delete()
        return Response({
            "success": "image deleted"
        })

class ClassifiedFavorites(APIView):
    
    def get(self, request):
        classifiedFavorites = ClassifiedFavorite.objects.filter(user=request.user).order_by('-id')
        vehicleId = self.request.query_params.get("vehicleId", None)
        listingId = self.request.query_params.get("listingId", None)

        if vehicleId:
            classifiedFavorites = classifiedFavorites.filter(vehicle_listing=vehicleId)
        if listingId:
            classifiedFavorites = classifiedFavorites.filter(listing=listingId)

        serializer = ClassifiedFavoriteSerializer(classifiedFavorites, many=True)

        return Response({
            "classified_favorites": serializer.data,
        })

    def post(self, request):
        vehicleId = request.data['vehicleId']
        listingId = request.data['listingId']
        vehicle_listing = None
        listing = None
        if vehicleId:
            vehicle_listing = VehicleListing.objects.get(id=vehicleId)
        if listingId:
            listing = Listing.objects.get(id=listingId)

        ClassifiedFavorite.objects.create(
            user=request.user,
            vehicle_listing=vehicle_listing,
            listing=listing,
        )

        return Response({
            "success": "Classified Favorite Created"
        })

    def delete(self, request):
        classifiedFavorite = ClassifiedFavorite.objects.filter(user=request.user)
        vehicleId = self.request.query_params.get("vehicleId", None)
        listingId = self.request.query_params.get("listingId", None)

        try:
            if vehicleId:
                classifiedFavorite = classifiedFavorite.filter(vehicle_listing=vehicleId).delete()
            if listingId:
                classifiedFavorite = classifiedFavorite.filter(listing=listingId).delete()

            return Response({
                "success": "Classified Favorite Deleted"
            })
        except:
            return Response({
                "error": "Classified Favorite Not Found"
            })  

class RaffleView(APIView):
    def get(self, request):
        tickets = RaffleEntry.objects.filter(user=request.user)
        serializer = RaffleEntrySerializer(tickets, many=True)
        return Response({
            "tickets": serializer.data
        })

@api_view(["POST",])
@permission_classes([AllowAny])
def MailSenderView(request):

    username = request.data['username']
    email = request.data['email']
    message = request.data['message']

    UM = "From - " + username + ' | message = ' + message
    send_mail('I have A Question', UM, email, ['LebaronGaleanaOfficial@gmail.com'], fail_silently=False)

    return Response()
