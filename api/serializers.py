from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import *
from .choices.listings import *
from rest_framework import generics
from django.db import transaction
import json

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

    class Meta:
        model = User
        fields = ('id','username', 'first_name', 'last_name', 'email', 'profile', 'date_joined')

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        profile = validated_data.get('profile')
        instance.profile.role = profile.get('role')
        instance.profile.status = profile.get('status')
        
        instance.save()
        return instance
    

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
    subtasks = SubTaskSerializer(many=True, read_only=True)
    subFactores = SubFactoresSerializer(many=True, read_only=True)
    subFuentes = SubFuentesSerializer(many=True, read_only=True)
    like_set = LikeCommentSerializer(many=True, read_only=True, source="likes")

    class Meta:
        model = NewPeticionCommentPost
        fields = '__all__'

    def get_likes_count(self, obj):
        return obj.likes.count()
        
class TaskSerializer(serializers.ModelSerializer):
    like_set = LikeSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    subtasks = SubTaskSerializer(many=True, read_only=True)
    subfuentes = SubFuentesSerializer(many=True, read_only=True)
    subfactores = SubFactoresSerializer(many=True, read_only=True)
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_user_image(self, obj):
        imagen_fija = ImagenFija.objects.filter(user=obj.user).last()
        
        if imagen_fija and imagen_fija.image:
            return imagen_fija.image.url
        return "No image available" 


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

class SharedTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    shared_by = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = SharedTask
        fields = ['id', 'task', 'shared_by', 'created_at', 'user_has_liked']

    def get_shared_by(self, obj):
        return {
            'id': obj.shared_by.id,
            'username': obj.shared_by.username,
            'email': obj.shared_by.email,
            'is_staff': obj.shared_by.is_staff
        }

    def get_user_has_liked(self, obj):
        user = self.context['request'].user
        return obj.task.like_set.filter(user=user).exists()


class PosttSerializer(serializers.ModelSerializer):
    replies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Postt
        fields = '__all__'
        

class SharedTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedTask
        fields = ['id', 'task', 'shared_by']


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
