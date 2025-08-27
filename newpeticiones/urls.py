# newpeticiones/urls.py
from django.urls import path
from .views import NewPeticionPostView, NewPeticionPostDetailsView, NewPeticionCommentView, NewPeticionCommentDetailsView

urlpatterns = [
    path('', NewPeticionPostView.as_view()),
    path('<int:peticion_id>/', NewPeticionPostDetailsView.as_view()),
    path('<int:peticion_id>/comments/', NewPeticionCommentView.as_view()),
    path('<int:peticion_id>/comments/<int:comment_id>/', NewPeticionCommentDetailsView.as_view()),
]
