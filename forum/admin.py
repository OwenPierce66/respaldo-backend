from django.contrib import admin
from .models import *

class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
admin.site.register(CommunityPost, CommunityPostAdmin)

class CommunityCommentAdmin(admin.ModelAdmin):
  list_display = ("id", "createdBy", "text")
admin.site.register(CommunityComment, CommunityCommentAdmin)
