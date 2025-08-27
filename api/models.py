from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from datetime import timedelta
import django.utils.timezone as timezone

from backend.storage_backends import SignatureStorage, ThumbnailStorage, BusinessPagePhotoStorage, ListingImageStorage, ProfileImageStorage, ImagenText, VideoStorage, ArchivosText


from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .choices.listings import *
from backend.storage_backends import DynamicImageStorage

#owen
class Portada(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)  
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=False) 

    def __str__(self):
        return self.title


class ImagenFija(models.Model):
    image = models.ImageField(storage=DynamicImageStorage(), null=True, blank=True)
    # image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Postt(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class NewCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CategoryP(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name='categoriesp', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class LikeP(models.Model):
    user = models.ForeignKey(User, related_name='likes_given', on_delete=models.CASCADE)
    profile = models.ForeignKey(User, related_name='likes_received', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'profile')

class TuModelo(models.Model):
    campo1 = models.CharField(max_length=100)
    campo2 = models.TextField()

class Hashtag(models.Model):
    text = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.text
    
class Categoryy(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    pch = models.TextField(blank=True, default='')
    username = models.TextField(blank=True, default='')
    categories = models.TextField(blank=True, default='')
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)
    share_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 

class NewPeticionCommentPost(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    post = models.ForeignKey('Task', on_delete=models.CASCADE)
    aportacion = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='aportacion_comments')  # Nuevo campo
    text = models.TextField()

    @property
    def children(self):
        return NewPeticionCommentPost.objects.filter(parent=self).order_by('-created_at')

    @property
    def is_parent(self):
        return self.parent is None

    @property
    def like_set(self):
        return LikeCommentPost.objects.filter(comment=self)

    @property
    def subtasks(self):
        return SubTaskCommentPost.objects.filter(parent_task=self)
    
    @property
    def subfuentes(self):
        return SubFuentesCommentPost.objects.filter(parent_task=self)

    @property
    def subfactores(self):
        return SubFactoresCommentPost.objects.filter(parent_task=self)

class LikeCommentPost(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(NewPeticionCommentPost, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    
class SubTaskCommentPost(models.Model):
    parent_task = models.ForeignKey(NewPeticionCommentPost, related_name='subtasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    link = models.TextField(blank=True, default='')   # Nuevo campo para enlaces
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)

class SubFactoresCommentPost(models.Model):
    parent_task = models.ForeignKey(NewPeticionCommentPost, related_name='subFactores', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    link = models.TextField(blank=True, default='')   # Nuevo campo para enlaces
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)

class SubFuentesCommentPost(models.Model):
    parent_task = models.ForeignKey(NewPeticionCommentPost, related_name='subFuentes', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    link = models.TextField(blank=True, default='')   # Nuevo campo para enlaces
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)
    
class SubTask(models.Model):
    parent_task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)
    link = models.TextField(blank=True, default='')   # Nuevo campo para enlaces

class SubFuentes(models.Model):
    parent_task = models.ForeignKey(Task, related_name='subfuentes', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)
    link = models.TextField(blank=True, default='')   # Nuevo campo para enlaces

class SubFactores(models.Model):
    parent_task = models.ForeignKey(Task, related_name='subfactores', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)
    link = models.TextField(blank=True, default='')   # Nuevo campo para enlaces

class NuevoTask(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, default='')
    description = models.TextField(blank=True, default='')
    completed = models.BooleanField(default=False)
    username = models.TextField(blank=True, default='')
    categories = models.TextField(blank=True, default='')
    image = models.ImageField(storage=ImagenText(), null=True, blank=True)
    video = models.FileField(storage=VideoStorage(), null=True, blank=True)

class Image(models.Model):
    task = models.ForeignKey(NuevoTask, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(storage=ImagenText(), blank=True, null=True)

class Video(models.Model):
    task = models.ForeignKey(NuevoTask, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(storage=VideoStorage(), blank=True, null=True)


class Favorito(models.Model):
    user = models.ForeignKey(User, related_name='favoritos', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='favoritos', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'task')

class pFavorito(models.Model):
    user = models.ForeignKey(User, related_name='usuario_que_favoritos', on_delete=models.CASCADE)  # El usuario que marca el favorito
    perfil = models.ForeignKey(User, related_name='perfiles_favoritos', on_delete=models.CASCADE)  # El perfil marcado como favorito
    
    class Meta:
        unique_together = ('user', 'perfil')


class Like(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE)

class Comment(models.Model):
    task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    userId = models.TextField()  # El contenido del comentario.
    # title = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    # parent_task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    description = models.TextField()
    # completed = models.BooleanField(default=False)
    username = models.TextField()
    image = models.ImageField(storage=ImagenText())


class LikeComment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)
    

class Imagen(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField()
    image = models.ImageField(storage=ImagenText())

class SharedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='shared_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task.title} shared by {self.shared_by.username}'



    
class ForumPostt(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # Otros campos...
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
# Create Token When New User Created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ForgotPasswordToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    token = models.TextField(unique=True)
    
    def get_token(self):
        return self.token
    
    def get_user(self):
        return self.user
    
    def is_expired(self):
        
        expiration_limit = timedelta(minutes=30)
        
        # using timezone.now() because django's auto_now_add uses it
        # time.time() or anything else create a 4 hour time difference
        return ( timezone.now() - self.created > expiration_limit )

class Group(models.Model):
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="leader")
    members = models.ManyToManyField(User, related_name="members", null=True, blank=True)
    description = models.TextField()

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class CalendarEventCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)


class CalendarEvent(models.Model):
    title = models.CharField(max_length=255)
    allDay = models.BooleanField(default=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    selectable = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    category = models.OneToOneField(to=CalendarEventCategory, on_delete=models.CASCADE, null=True)


class ProfileImage(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=ProfileImageStorage())

# Profile Model That Extends User Model
class Profile(models.Model):
    USER = 1
    EDITOR = 2
    ADMIN = 3
    GALEANA_BIZ_DRIVER = 4
    ROLE_CHOICES = (
        (USER, 'User'),
        (EDITOR, 'Editor'),
        (ADMIN, 'Admin'),
        (GALEANA_BIZ_DRIVER, 'Galeana Biz driver'),
    )

    PENDING = 1
    APPROVED = 2
    BANNED = 3
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (BANNED, 'Banned'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=USER)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=APPROVED)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True) # validators should be a list
    subscriptionActive = models.BooleanField(default=False)
    freeAccount = models.BooleanField(default=False)
    head_of_household = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    calendar_event_categories = models.ManyToManyField(CalendarEventCategory, blank=True)
    image = models.URLField(blank=True, null=True)
   
    
    def get_status(self, obj):
        return obj.get_status_display()
    
    def get_role(self, obj):
        return obj.get_role_display()
    

class YOI_Registration(models.Model):
    SIZE_CHOICES = (
        (0, "XS"),
        (1, "S"),
        (2, "M"),
        (3, "L"),
        (4, "XL"),
        (5, "12/14"),
        (6, "14/16"),
        (7, "Other")
    )
    GENDER_OPTIONS = (
        (0, "Male"),
        (1, "Female"),
        (2, "Unknown")
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True) # validators should be a list
    allergies = models.CharField(max_length=1000, blank=True, null=True)
    size = models.PositiveSmallIntegerField(choices=SIZE_CHOICES, default=2)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    payment_complete = models.BooleanField(default=False)
    gender = models.PositiveSmallIntegerField(choices=GENDER_OPTIONS, default=2)
    translation_assistance = models.BooleanField(default=False)
    spanish_shirt = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name


# Will Create Or Update Profile Through User Model
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Error(models.Model):
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.CharField(max_length=1000, blank=True, null=True)


class Item(models.Model):
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    TYPE_CHOICES = (
        ('blog', 'blog'),
        ('ad', 'ad'),
        ('announcement', 'announcement')
    )
    post_type = models.CharField(max_length=25, choices=TYPE_CHOICES, default='blog')
    title = models.CharField(max_length=150, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    items = models.ManyToManyField(Item)
    contact = models.CharField(max_length=150, blank=True, null=True)
    submittedOn = models.DateTimeField(auto_now=True)
    imageURL = models.URLField(blank=True, null=True)


class Thumbnail(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=ThumbnailStorage())

class Blog(models.Model):
    DRAFT = 1
    PUBLISHED = 2
    HIDDEN = 3
    STATUS_CHOICES = (
        ( DRAFT, "Draft" ),
        ( PUBLISHED, "Published" ),
        ( HIDDEN , "Hidden")
    )
    PRIVATE = 1
    PUBLIC = 2
    SECURITY_CHOICES = (
        ( PRIVATE, "Private" ),
        ( PUBLIC, "Public" )
    )
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=200, blank=True, null=True)
    thumb_nail = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="createdBy")
    lastUpdatedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lastUpdatedBy")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField( choices=STATUS_CHOICES, default=DRAFT)
    security = models.SmallIntegerField( choices=SECURITY_CHOICES, default=PRIVATE )
    
class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=SignatureStorage())

class Petition(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class PetitionEntry(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True)
    signature = models.URLField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True)

class RepresentativeSurveyEntry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    infrastructure_representative = models.BooleanField()
    security_representative = models.BooleanField()
    health_representative = models.BooleanField()
    law_representative = models.BooleanField()
    culture_representative = models.BooleanField()
    education_representative = models.BooleanField()
    sports_representative = models.BooleanField()
    treasury_representative = models.BooleanField()
    social_representative = models.BooleanField()
    info_tech_representative = models.BooleanField()
    misc_representative = models.BooleanField()

class CredencialSurveyEntry(models.Model):
    
    # Crendencial is a mexican voting license
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_credencial = models.BooleanField()
    expiration_date = models.IntegerField( null=True, blank=True)

class VotingForAmmonSurveyEntry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    voting_for_ammon = models.BooleanField()
    comment = models.TextField(max_length=300, null=True, blank=True)


class AgreementSubmission(models.Model):
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agreement = models.CharField(max_length=1000, null=True, blank=True)


class Currency(models.Model):
    name = models.CharField(max_length=1000)
    sell = models.DecimalField(max_digits=100, decimal_places=3)
    buy = models.DecimalField(max_digits=100, decimal_places=3)

    


class BusinessPagePhoto(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=BusinessPagePhotoStorage())


class BusinessPage(models.Model):
    PENDING = 1
    LIVE = 2
    STATUS_CHOICES = (
        ( PENDING, "Pending" ),
        ( LIVE, "Live" )
    )
    banner = models.ForeignKey(BusinessPagePhoto, models.SET_NULL, blank=True, null=True, related_name="banner")
    name = models.TextField()
    location = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=160)
    hours = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(BusinessPagePhoto, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    status = models.PositiveSmallIntegerField( choices=STATUS_CHOICES, default=PENDING )

class BusinessPagePost(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(BusinessPagePhoto, blank=True, null=True)
    page = models.ForeignKey(BusinessPage, on_delete=models.CASCADE)

class Directory(models.Model):
    name = models.TextField()
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
    phone_number = models.CharField(max_length=100, blank=True, null=True) # validators should be a list
    category = models.TextField()
    businessPage = models.ForeignKey(BusinessPage, models.SET_NULL, blank=True, null=True)

class StripeCustomer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.stripeCustomerId


class RaffleEntry(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripePaymentIntent = models.CharField(max_length=255, blank=True, null=True)
    stripeSubscriptionId = models.CharField(max_length=255, blank=True, null=True)
    payments = models.IntegerField(default=0)

    def __str__(self):
        return self.stripeCustomerId

class YOI_Assistant(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phoneNumber = models.CharField(max_length=255, null=True, blank=True)
    attended = models.CharField(max_length=255)
    years = models.CharField(max_length=255)
    reasonOne = models.CharField(max_length=1500)
    reasonTwo = models.CharField(max_length=1500)
    giftOne = models.CharField(max_length=1500)
    giftTwo = models.CharField(max_length=1500)
    giftThree = models.CharField(max_length=1500)
    suggestionOne = models.CharField(max_length=1500)
    suggestionTwo = models.CharField(max_length=1500)
    suggestionThree = models.CharField(max_length=1500)
    classOne = models.CharField(max_length=1500)
    classTwo = models.CharField(max_length=1500)
    signature = models.CharField(max_length=1500)
    created = models.DateField(auto_now_add=True)
    



class ListingImage(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=ListingImageStorage())

    def delete(self):
        self.file.delete(save=False)
        super().delete()
    

class Listing(models.Model):
    # Listing Info
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField()
    favorites = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    
    # Contact Info 
    callEnabled = models.BooleanField(default=True)
    contact_email = models.CharField(max_length=200, blank=True, null=True)
    contact_number = models.CharField(max_length=100, blank=True, null=True)
    emailEnabled = models.BooleanField(default=True)
    textEnabled = models.BooleanField(default=True)

    # Item Info
    category = models.PositiveSmallIntegerField( choices=LISTING_CATEGORIES)
    condition = models.PositiveSmallIntegerField( choices=LISTING_CONDITION)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(ListingImage, blank=True, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    title = models.CharField(max_length=250)


class VehicleListing(models.Model):
    # Listing Info
    available = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    expire_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    favorites = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    views = models.IntegerField(default=0)

    # Contact Info
    callEnabled = models.BooleanField(default=True)
    contact_email = models.CharField(max_length=200, blank=True, null=True)
    contact_number = models.CharField(max_length=100, blank=True, null=True)
    emailEnabled = models.BooleanField(default=True)
    textEnabled = models.BooleanField(default=True)

    # Vehicle Info
    body_style = models.PositiveSmallIntegerField( choices=BODY_STYLE)
    exterior_color = models.PositiveSmallIntegerField( choices=COLOR_OPTIONS)
    exterior_condition = models.PositiveSmallIntegerField( choices=VEHICLE_CONDITION)
    fuel_type = models.PositiveSmallIntegerField( choices=FUEL_TYPE)
    interior_color = models.PositiveSmallIntegerField( choices=COLOR_OPTIONS)
    interior_condition = models.PositiveSmallIntegerField( choices=VEHICLE_CONDITION)
    location = models.TextField(blank=True, null=True)
    make = models.PositiveSmallIntegerField( choices=VEHICLE_MAKE)
    mileage = models.IntegerField(blank=True, null=True)
    model = models.CharField(max_length=1500, blank=True, null=True)
    photos = models.ManyToManyField(ListingImage, blank=True, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    transmission = models.PositiveSmallIntegerField( choices=TRANSMISSION_TYPE)
    trim = models.CharField(max_length=1500, blank=True, null=True)
    vin = models.CharField(max_length=20, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

class ClassifiedFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    vehicle_listing = models.ForeignKey(VehicleListing, on_delete=models.CASCADE, blank=True, null=True)
