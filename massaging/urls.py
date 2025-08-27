from django.urls import path
from .views import *

urlpatterns = [
    path('users/', user_list, name='user-list'),
    path('messages/', message_list, name='message-list'),
    path('messages/<int:message_id>/like/', like_unlike_message, name='like_unlike_message'),
    path('messages/<int:message_id>/liked_users/', users_who_liked_message, name='users_who_liked_message'),
    path('groupss/', list_groups, name='list-groups'),
    path('groupss/create/', create_group, name='create-group'),
    path('groupss/<int:group_id>/add_member/', add_member, name='add-member'),
    path('groupss/<int:group_id>/remove_member/', remove_member, name='remove-member'),
    path('groupss/<int:group_id>/make_admin/', make_admin, name='make-admin'),
    path('groupss/<int:group_id>/messages/', group_messages, name='group-messages'),
    path('groupss/<int:group_id>/send_message/', send_group_message, name='send-group-message'),
]