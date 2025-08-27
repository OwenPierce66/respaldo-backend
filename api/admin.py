from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ngettext

from .models import *

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class StripeCustomerInline(admin.StackedInline):
    model = StripeCustomer
    can_delete = False
    verbose_name_plural = 'Stripe Customers'
    fk_name = 'user'



class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, StripeCustomerInline)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class YOI_RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'first_name', 'payment_complete')
    actions = ('mark_payment_as_incomplete',)

    def mark_payment_as_incomplete(self, request, queryset):
        updated = queryset.update(payment_complete=False)
        self.message_user(request, ngettext(
            '%d YOI kid registration was successfully marked with their payment as incomplete.',
            '%d YOI kid registrations were successfully marked with their payment as incomplete.',
            updated,
        ) % updated, messages.SUCCESS)

admin.site.register(YOI_Registration, YOI_RegistrationAdmin)

admin.site.register(NuevoTask) 

class ErrorAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'user')
admin.site.register(Error, ErrorAdmin)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
admin.site.register(Item, ItemAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_type', 'title', 'submittedOn')
admin.site.register(Post, PostAdmin)

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'createdBy', 'updated', 'title', 'status', 'security')
admin.site.register(Blog, BlogAdmin)

class PetitionAdmin(admin.ModelAdmin):
    list_display = ('id','name')
admin.site.register(Petition, PetitionAdmin)

class PetitionEntryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'phone_number', 'date')
admin.site.register(PetitionEntry, PetitionEntryAdmin)

class UploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')
admin.site.register(Upload, UploadAdmin)

class AgreementSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
admin.site.register(AgreementSubmission, AgreementSubmissionAdmin)

class RepresentativeSurveyEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'infrastructure_representative', 'security_representative', 'health_representative', 'law_representative', 'culture_representative', 'education_representative', 'sports_representative', 'treasury_representative', 'social_representative', 'info_tech_representative', 'misc_representative' )
admin.site.register(RepresentativeSurveyEntry, RepresentativeSurveyEntryAdmin)

class CredencialSurveyEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_credencial', 'expiration_date')
admin.site.register(CredencialSurveyEntry, CredencialSurveyEntryAdmin)

class VotingForAmmonSurveyEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'voting_for_ammon', 'comment')
admin.site.register(VotingForAmmonSurveyEntry, VotingForAmmonSurveyEntryAdmin)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sell', 'buy')
admin.site.register(Currency, CurrencyAdmin)

class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
admin.site.register(Directory, DirectoryAdmin)

class BusinessPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
admin.site.register(BusinessPage, BusinessPageAdmin)

class BusinessPagePostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
admin.site.register(BusinessPagePost, BusinessPagePostAdmin)

class BusinessPagePhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')
admin.site.register(BusinessPagePhoto, BusinessPagePhotoAdmin)

admin.site.register(StripeCustomer)
admin.site.register(RaffleEntry)

class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start', 'end')
admin.site.register(CalendarEvent, CalendarEventAdmin)

admin.site.register(YOI_Assistant)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'leader')
admin.site.register(Group, GroupAdmin)

class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'created')
admin.site.register(GroupMessage, GroupMessageAdmin)
admin.site.register(ListingImage)

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'price', 'category')
admin.site.register(Listing, ListingAdmin)

class VehicleListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'make', 'model', 'price')
admin.site.register(VehicleListing, VehicleListingAdmin)

admin.site.register(ClassifiedFavorite)