from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_unlike_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    like, created = MessageLike.objects.get_or_create(user=request.user, message=message)
    if not created:
        like.delete()
        return Response({'status': 'like removed'})
    return Response({'status': 'like added'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_who_liked_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    users = [like.user for like in message.likes.all()]
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def message_list(request):
    if request.method == 'GET':
        user_id = request.query_params.get('user_id')
        page = int(request.query_params.get('page', 1))
        page_size = 10  # You can adjust the page size as needed

        try:
            if user_id:
                messages = Message.objects.filter(
                    Q(sender_id=request.user.id, receiver_id=user_id) |
                    Q(sender_id=user_id, receiver_id=request.user.id)
                ).order_by('-timestamp')
            else:
                messages = Message.objects.all().order_by('-timestamp')

            start = (page - 1) * page_size
            end = start + page_size
            paginated_messages = messages[start:end]

            serializer = MessageSerializer(paginated_messages, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'POST':
        try:
            data = request.data.copy()
            data['sender'] = request.user.id
            receiver_id = data.get('receiver')
            if receiver_id:
                receiver = User.objects.get(id=receiver_id)
                data['receiver'] = receiver_id  # Usar el ID directamente
            else:
                return Response({"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = MessageSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save(sender=request.user, receiver=receiver)  # Guardar con el remitente y el receptor como objetos
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Receiver not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    group = Group.objects.create(name=name, created_by=request.user)
    GroupMembership.objects.create(user=request.user, group=group, is_admin=True)
    return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request, group_id):
    group = Group.objects.get(id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
        return Response({'error': 'Only admins can add members'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    user = User.objects.get(id=user_id)
    GroupMembership.objects.create(user=user, group=group)
    return Response({'status': 'member added'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member(request, group_id):
    group = Group.objects.get(id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
        return Response({'error': 'Only admins can remove members'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    user = User.objects.get(id=user_id)
    GroupMembership.objects.filter(user=user, group=group).delete()
    return Response({'status': 'member removed'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_admin(request, group_id):
    group = Group.objects.get(id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
        return Response({'error': 'Only admins can make other admins'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    user = User.objects.get(id=user_id)
    membership = GroupMembership.objects.get(user=user, group=group)
    membership.is_admin = True
    membership.save()
    return Response({'status': 'user promoted to admin'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_groups(request):
    groups = Group.objects.filter(members=request.user)
    return Response(GroupSerializer(groups, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_messages(request, group_id):
    group = Group.objects.get(id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response({'error': 'You are not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    messages = GroupMessage.objects.filter(group=group).order_by('-timestamp')
    return Response(GroupMessageSerializer(messages, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_group_message(request, group_id):
    group = Group.objects.get(id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response({'error': 'You are not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    content = request.data.get('content')
    image = request.data.get('image')
    video = request.data.get('video')
    message = GroupMessage.objects.create(group=group, sender=request.user, content=content, image=image, video=video)
    return Response(GroupMessageSerializer(message).data, status=status.HTTP_201_CREATED)