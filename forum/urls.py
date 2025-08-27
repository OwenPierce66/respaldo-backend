from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    path('', CommunityPostView.as_view()),
    path('<int:post_id>/', CommunityPostDetailsView.as_view()),
    path('<int:post_id>/comments/', CommunityCommentView.as_view()),
    path('<int:post_id>/comments/<int:comment_id>/', CommunityCommentDetailsView.as_view()),
]