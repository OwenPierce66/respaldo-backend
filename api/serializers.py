from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import *
from .choices.listings import *
from rest_framework import generics
from django.db import transaction
import json
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import default_storage


def file_to_abs_url(file_or_str, request=None):
    """
    Convierte FieldFile o string a URL absoluta (https://tu-dominio/...).
    Soporta storages custom (file.url) y paths string.
    """
    if not file_or_str:
        return None

    # 1) FieldFile -> .url
    if hasattr(file_or_str, "url"):
        url = file_or_str.url
    else:
        url = str(file_or_str).strip()
        if not url:
            return None

        # Si ya es absoluta
        if url.startswith(("http://", "https://")):
            return url

        media_url = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/")

        # Si viene como "imagenfija/xxx.jpg" => intenta resolver via storage
        if not url.startswith("/") and not url.startswith(media_url + "/"):
            try:
                url = default_storage.url(url.lstrip("/"))
            except Exception:
                url = f"{media_url}/{url.lstrip('/')}"
        elif not url.startswith("/"):
            url = "/" + url

    # 2) Forzar absoluta si hay request y no es http(s)
    if request and url and not url.startswith(("http://", "https://")):
        if not url.startswith("/"):
            url = "/" + url
        return request.build_absolute_uri(url)

    return url

class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class NewCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewCategory
        fields = '__all__'

class CategoryPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryP
        fields = ['id', 'name', 'user']
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SimpleUserSerializer(serializers.ModelSerializer):
    categoriesp = CategoryPSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'categoriesp', 'likes_count', 'user_image', 'has_liked')

    def get_likes_count(self, obj):
        return LikeP.objects.filter(profile=obj).count()

    def get_user_image(self, obj):
        imagen_fija = ImagenFija.objects.filter(user=obj).last()
        if imagen_fija and imagen_fija.image:
            return imagen_fija.image.url
        return "No image available"

    def get_has_liked(self, obj):
        request = self.context.get('request', None)  
        if request and request.user.is_authenticated:
            return LikeP.objects.filter(user=request.user, profile=obj).exists()
        return False  

        


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    shared = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "avatar_url", "liked", "shared")

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        name = getattr(obj, "latest_imagenfija_image", None)  # viene de tu Subquery

        if not name:
            return None

        # 1) Si es un ImageFieldFile / File, usa su .url
        if hasattr(name, "url"):
            url = name.url
        else:
            # 2) Es un string (puede ser 'imagenfija/yo.jpg', '/media/imagenfija/yo.jpg' o ya http(s))
            url = str(name).strip()
            if not url:
                return None

            # 2.a) Si YA es http(s), úsala tal cual
            if url.startswith(("http://", "https://")):
                return url

            # 2.b) Si ya empieza por MEDIA_URL o por '/media/', déjala así (normaliza a absoluto si hace falta)
            media_url = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/")
            if url.startswith(media_url + "/") or url.startswith("/media/"):
                # ok
                pass
            else:
                # 2.c) Es una ruta de storage como 'imagenfija/yo.jpg' -> conviértela a '/media/...'
                try:
                    url = default_storage.url(url.lstrip("/"))
                except Exception:
                    # fallback por si el storage no resolvió
                    url = f"{media_url}/{url.lstrip('/')}"

        # 3) Asegura absoluta con host cuando no es http(s)
        if request and url and not url.startswith(("http://", "https://")):
            if not url.startswith("/"):
                url = "/" + url  # <- evita el bug de concatenarse al path del endpoint actual
            return request.build_absolute_uri(url)

        return url

    def get_liked(self, obj):
        return bool(getattr(obj, "liked", False))

    def get_shared(self, obj):
        return bool(getattr(obj, "shared", False))
    

class TuModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuModelo
        fields = '__all__'
        

class ImagenSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Imagen
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'

class CategoryySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoryy
        fields = ['id', 'name']

class SubTaskSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    class Meta:
        model = SubTask
        fields = '__all__'

class SubFuentesSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    
    class Meta:
        model = SubFuentes
        fields = '__all__'

class SubFactoresSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    
    class Meta:
        model = SubFactores
        fields = '__all__'


class SubTaskCommentPostSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=NewPeticionCommentPost.objects.all())
    class Meta:
        model = SubTaskCommentPost
        fields = '__all__'

class SubFuentesCommentPostSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=NewPeticionCommentPost.objects.all())
    class Meta:
        model = SubFuentesCommentPost
        fields = '__all__'

class SubFactoresCommentPostSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=NewPeticionCommentPost.objects.all())
    class Meta:
        model = SubFactoresCommentPost
        fields = '__all__'

class SubFuentesPCHPostSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=NewPeticionCommentPost.objects.all())
    class Meta:
        model = SubFuentesCommentPost
        fields = '__all__'

class SubFactoresPCHPostSerializer(serializers.ModelSerializer):
    parent_task = serializers.PrimaryKeyRelatedField(queryset=NewPeticionCommentPost.objects.all())
    class Meta:
        model = SubFactoresCommentPost
        fields = '__all__'


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CreateNewPeticionCommentSerializer(serializers.ModelSerializer):
    aportacion = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False, allow_null=True)

    class Meta:
        model = NewPeticionCommentPost
        fields = "__all__"

    def get_likes_count(self, obj):
        return getattr(obj, 'likes_count', obj.likes.count())

class LikeCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = LikeCommentPost
        fields = '__all__'

class NewPeticionCommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    children = RecursiveField(many=True)
    is_parent = serializers.ReadOnlyField()
    likes_count = serializers.SerializerMethodField()

    # ✅ usa los serializers de CommentPost
    subtasks = SubTaskCommentPostSerializer(many=True, read_only=True)
    subFuentes = SubFuentesCommentPostSerializer(many=True, read_only=True)
    subFactores = SubFactoresCommentPostSerializer(many=True, read_only=True)

    like_set = LikeCommentSerializer(many=True, read_only=True, source="likes")

    # ✅ NUEVO: Reels para aportaciones (comentarios) también
    primary_video = serializers.SerializerMethodField()
    primary_media = serializers.SerializerMethodField()
    media_options = serializers.SerializerMethodField()

    class Meta:
        model = NewPeticionCommentPost
        fields = '__all__'

    def get_likes_count(self, obj):
        return obj.likes.count()

    def _clip(self, kind, obj_id, video_file, title="", parent_comment=None, parent_task=None):
        request = self.context.get("request")
        return {
            "kind": kind,  # "comment_subtask" | "comment_subfuente" | "comment_subfactor"
            "id": obj_id,
            "parent_comment": parent_comment,
            "parent_task": parent_task,
            "title": title or "",
            "video": file_to_abs_url(video_file, request=request),
        }

    def get_media_options(self, obj):
        opts = []
        # Nota: aquí NO hay obj.video, sólo videos en sus sub-objetos

        for st in obj.subtasks.all():
            if getattr(st, "video", None):
                opts.append(self._clip(
                    "comment_subtask", st.id, st.video,
                    title=getattr(st, "title", ""),
                    parent_comment=obj.id,
                    parent_task=obj.post_id
                ))

        for sf in obj.subFuentes.all():
            if getattr(sf, "video", None):
                opts.append(self._clip(
                    "comment_subfuente", sf.id, sf.video,
                    title=getattr(sf, "title", ""),
                    parent_comment=obj.id,
                    parent_task=obj.post_id
                ))

        for sc in obj.subFactores.all():
            if getattr(sc, "video", None):
                opts.append(self._clip(
                    "comment_subfactor", sc.id, sc.video,
                    title=getattr(sc, "title", ""),
                    parent_comment=obj.id,
                    parent_task=obj.post_id
                ))

        return opts

    def _pick_primary(self, obj):
        # Orden auto para comentarios: subtask -> subfuente -> subfactor
        for st in obj.subtasks.all():
            if getattr(st, "video", None):
                return ("comment_subtask", st.id, st.video)

        for sf in obj.subFuentes.all():
            if getattr(sf, "video", None):
                return ("comment_subfuente", sf.id, sf.video)

        for sc in obj.subFactores.all():
            if getattr(sc, "video", None):
                return ("comment_subfactor", sc.id, sc.video)

        return (None, None, None)

    def get_primary_video(self, obj):
        kind, _id, v = self._pick_primary(obj)
        request = self.context.get("request")
        return file_to_abs_url(v, request=request)

    def get_primary_media(self, obj):
        kind, _id, v = self._pick_primary(obj)
        if not v:
            return None
        return {"kind": kind, "id": _id}



class TaskSerializer(serializers.ModelSerializer):
    like_set = LikeSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    subtasks = SubTaskSerializer(many=True, read_only=True)
    subfuentes = SubFuentesSerializer(many=True, read_only=True)
    subfactores = SubFactoresSerializer(many=True, read_only=True)
    user_image = serializers.SerializerMethodField()
    shared_by_list = serializers.SerializerMethodField()

    # ✅ NUEVO
    primary_video = serializers.SerializerMethodField()
    primary_media = serializers.SerializerMethodField()
    media_options = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_likes_count(self, obj):
        return getattr(obj, 'likes_count', obj.like_set.count())

    def get_user_image(self, obj):
        imagen_fija = ImagenFija.objects.filter(user=obj.user).last()
        if imagen_fija and imagen_fija.image:
            return imagen_fija.image.url
        return None

    def get_shared_by_list(self, obj):
        request = self.context.get("request")

        # cache por serializer-instance (evita N consultas repetidas)
        if not hasattr(self, "_share_img_cache"):
            self._share_img_cache = {}

        out = []

        # Opcional: orden para que "último que compartió" sea el último
        for st in obj.shared_tasks.all().order_by("id"):
            sb = st.shared_by
            if not sb:
                out.append({
                    "id": None,
                    "username": "unknown",
                    "description": st.description or "",
                    "user_image": None,
                })
                continue

            # cache de imagen por user id
            if sb.id not in self._share_img_cache:
                imagen_fija = ImagenFija.objects.filter(user=sb).order_by("-id").first()
                if imagen_fija and imagen_fija.image:
                    url = imagen_fija.image.url  # normalmente "/media/..."
                    # si quieres absoluta (opcional):
                    if request:
                        url = request.build_absolute_uri(url)
                    self._share_img_cache[sb.id] = url
                else:
                    self._share_img_cache[sb.id] = None

            out.append({
                "id": sb.id,
                "username": getattr(sb, "username", "unknown"),
                # ojo: exponer email/is_staff en feed no suele ser buena idea; si lo ocupas, déjalo
                "email": getattr(sb, "email", None),
                "is_staff": getattr(sb, "is_staff", False),
                "description": st.description or "",
                "user_image": self._share_img_cache[sb.id],  # ✅ CLAVE
            })

        return out
    # ---------------------------
    # ✅ REELS: media index
    # ---------------------------
    def _clip(self, kind, obj_id, video_file, title="", parent_task=None):
        request = self.context.get("request")
        return {
            "kind": kind,  # "task" | "subtask" | "subfuente" | "subfactor"
            "id": obj_id,
            "parent_task": parent_task,
            "title": title or "",
            "video": file_to_abs_url(video_file, request=request),
        }

    def get_media_options(self, obj):
        opts = []

        # 1) video del task
        if getattr(obj, "video", None):
            opts.append(self._clip("task", obj.id, obj.video, title=getattr(obj, "title", ""), parent_task=obj.id))

        # 2) videos de subtasks (aportaciones)
        for st in obj.subtasks.all():
            if getattr(st, "video", None):
                opts.append(self._clip("subtask", st.id, st.video, title=getattr(st, "title", ""), parent_task=obj.id))

        # 3) videos de subfuentes
        for sf in obj.subfuentes.all():
            if getattr(sf, "video", None):
                opts.append(self._clip("subfuente", sf.id, sf.video, title=getattr(sf, "title", ""), parent_task=obj.id))

        # 4) videos de subfactores
        for sc in obj.subfactores.all():
            if getattr(sc, "video", None):
                opts.append(self._clip("subfactor", sc.id, sc.video, title=getattr(sc, "title", ""), parent_task=obj.id))

        return opts

    def _pick_primary(self, obj):
        # Orden “auto”: Task.video -> SubTask -> SubFuente -> SubFactor
        if getattr(obj, "video", None):
            return ("task", obj.id, obj.video)

        for st in obj.subtasks.all():
            if getattr(st, "video", None):
                return ("subtask", st.id, st.video)

        for sf in obj.subfuentes.all():
            if getattr(sf, "video", None):
                return ("subfuente", sf.id, sf.video)

        for sc in obj.subfactores.all():
            if getattr(sc, "video", None):
                return ("subfactor", sc.id, sc.video)

        return (None, None, None)

    def get_primary_video(self, obj):
        kind, _id, v = self._pick_primary(obj)
        request = self.context.get("request")
        return file_to_abs_url(v, request=request)

    def get_primary_media(self, obj):
        kind, _id, v = self._pick_primary(obj)
        if not v:
            return None
        return {"kind": kind, "id": _id}




class SharedTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    shared_by = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    shared_by_username = serializers.CharField(source='shared_by.username', read_only=True)

    class Meta:
        model = SharedTask
        fields = ['id', 'task', 'shared_by', 'shared_by_username', 'created_at', 'description', 'user_has_liked']


    def get_user_has_liked(self, obj):
        user = self.context['request'].user
        return obj.task.like_set.filter(user=user).exists()


    def get_shared_by(self, obj):
        return {
            'id': obj.shared_by.id,
            'username': obj.shared_by.username,
            'email': obj.shared_by.email,
            'is_staff': obj.shared_by.is_staff
        }


class TaskFeedSerializer(serializers.ModelSerializer):
    shared_tasks = SharedTaskSerializer(many=True, read_only=True)
    shared_by_list = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'pch', 'username', 'categories',
            'image', 'video', 'share_count', 'created_at',
            'shared_tasks', 'shared_by_list'
        )

    def get_shared_by_list(self, obj):
        # Solo lista de usuarios que compartieron esta tarea
        return [share.shared_by.username if share.shared_by else 'unknown' for share in obj.shared_tasks.all()]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'id') 
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('video', 'id') 
    
class NuevoTaskSerializer(serializers.ModelSerializer):
    like_set = LikeSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NuevoTask
        fields = '__all__'
    
    def get_likes_count(self, obj):
        return obj.like_set.count()

class FavoritoReadSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True) 
    
    class Meta:
        model = Favorito
        fields = '__all__'

    
class FavoritoSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    
    class Meta:
        model = Favorito
        fields =  '__all__'  

class pFavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = pFavorito
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class PosttSerializer(serializers.ModelSerializer):
    replies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Postt
        fields = '__all__'
        

class SharedTaskCreateSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = SharedTask
        fields = ['id', 'task', 'shared_by', 'description', 'created_at']
        read_only_fields = ['id', 'shared_by', 'created_at']

    def create(self, validated_data):
        # Asegura que shared_by siempre venga del context (request.user)
        user = self.context['request'].user
        validated_data['shared_by'] = user
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'phone_number']  

class UserDetailsSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class PortadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portada
        fields = ['id', 'title', 'image', 'user'] 
        read_only_fields = ['user'] 

class ImagenFijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenFija
        fields = ['id', 'image', 'created_at']
    
    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("La imagen es obligatoria")
        return value
# auth

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def validate(self, data):
        # Username and password required enforced by model
        if 'type' in self.context and self.context['type'] == 'account':
            required_fields = ['email']
        else:
            required_fields = ['email', 'first_name', 'last_name']

        for key in required_fields:
            if key not in data or data[key] == '':
                raise serializers.ValidationError({ key: "This field may not be blank" })

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                "email": "This email is already being used for a different account, please login with that account. If you need help logging in, go to the contact page."
            })

        return data

    def save(self):
            user = User(
                email = self.validated_data['email'],
                username=self.validated_data['username'],
                first_name=self.validated_data['first_name'],
                last_name=self.validated_data['last_name']
            )
            user.set_password(self.validated_data['password'])
            user.save()
            return user

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields =['id', 'name', 'price']


class PostSerializer(serializers.ModelSerializer):
    items = ItemSerializer(read_only=True, many=True)
    class Meta:
        model = Post
        fields = ['id', 'post_type', 'title', 'content', 'items', 'contact', 'submittedOn', 'imageURL']

class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        return self._choices[obj]


    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)

class BlogPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"
        
class BlogSerializer(serializers.ModelSerializer):
    status = ChoiceField(choices=Blog.STATUS_CHOICES)
    security = ChoiceField(choices=Blog.SECURITY_CHOICES)
    createdBy = UserSerializer()
    lastUpdatedBy = UserSerializer()

    class Meta:
        model = Blog
        fields = [
            'id', 'createdBy', 'lastUpdatedBy', 'created', 'updated',
            'title', 'summary', 'thumb_nail', 'content', 'status',
            'security'
            ]
            
class PetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Petition
        fields = "__all__"
    
class PetitionEntrySerializer(serializers.ModelSerializer):
    # petition = PetitionSerializer()

    class Meta:
        model = PetitionEntry
        fields = ['id', 'date', 'name', 'phone_number', 'signature', 'petition']

class PetitionEntryGETSerializer(serializers.ModelSerializer):
    petition = PetitionSerializer()

    class Meta:
        model = PetitionEntry
        fields = ['id', 'date', 'name', 'phone_number', 'signature', 'petition']

class AgreementSubmissionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = AgreementSubmission
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'buy', 'sell']
    



class BusinessPagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPagePhoto
        fields = "__all__"


class BusinessPageSerializer(serializers.ModelSerializer):
    banner = BusinessPagePhotoSerializer(read_only=True)
    photos = BusinessPagePhotoSerializer(read_only=True, many=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = BusinessPage
        fields = "__all__"


class BusinessPagePostSerializer(serializers.ModelSerializer):
    page = BusinessPageSerializer()
    
    class Meta:
        model = BusinessPagePost
        fields = "__all__"

class DirectorySerializer(serializers.ModelSerializer):
    businessPage = BusinessPageSerializer(read_only=True)

    class Meta:
        model = Directory
        fields = "__all__"

class StripeCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeCustomer
        fields = "__all__"


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = "__all__"


class CalendarEventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEventCategory
        fields = "__all__"


class YOI_AssistantSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    allReasons = serializers.SerializerMethodField('all_reasons')
    allSuggestions = serializers.SerializerMethodField('all_suggestions')
    allGifts = serializers.SerializerMethodField('all_gifts')
    allClasses = serializers.SerializerMethodField('all_classes')

    class Meta:
        model = YOI_Assistant
        fields = ("__all__")

    def get_name(self, instance):
        return "{} {}".format(instance.user.first_name, instance.user.last_name)

    def all_reasons(self, instance):
        return "\n".join([instance.reasonOne, instance.reasonTwo])

    def all_gifts(self, instance):
        return "\n".join([instance.giftOne, instance.giftTwo, instance.giftThree])

    def all_suggestions(self, instance):
        return "\n".join([instance.suggestionOne, instance.suggestionTwo, instance.suggestionThree])

    def all_classes(self, instance):
        return "\n".join([instance.classOne, instance.classTwo])

class YOI_RegistrationSerializer(serializers.ModelSerializer):
    parent = UserSerializer()
    class Meta:
        model = YOI_Registration
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
    leader = UserSerializer()
    members = UserSerializer(many=True)
    class Meta:
        model = Group
        fields = "__all__"

class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class GroupMessageSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    class Meta:
        model = GroupMessage
        fields = "__all__"

class GroupCreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = "__all__"

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = "__all__"
    
class ListingSerializer(serializers.ModelSerializer):
    photos = ListingImageSerializer(read_only=True, many=True)
    
    class Meta:
        model = Listing
        fields = "__all__"

class VehicleListingSerializer(serializers.ModelSerializer):
    photos = ListingImageSerializer(read_only=True, many=True)
 
    class Meta:
        model = VehicleListing
        fields = "__all__"

class ClassifiedFavoriteSerializer(serializers.ModelSerializer):
    vehicle_listing = VehicleListingSerializer()
    listing = ListingSerializer()

    class Meta:
        model = ClassifiedFavorite
        fields = "__all__"

class RaffleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RaffleEntry
        fields = "__all__"
