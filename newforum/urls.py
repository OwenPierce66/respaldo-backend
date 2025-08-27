from django.urls import path
from .views import NewCommunityPostView, NewCommunityPostDetailsView, NewCommunityCommentView, NewCommunityCommentDetailsView

urlpatterns = [
    path('', NewCommunityPostView.as_view()),
    path('<int:post_id>/', NewCommunityPostDetailsView.as_view()),
    path('<int:post_id>/comments/', NewCommunityCommentView.as_view()),
    path('<int:post_id>/comments/<int:comment_id>/', NewCommunityCommentDetailsView.as_view()),
]
