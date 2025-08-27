from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # MISC URLS
    path('', DashboardView.as_view(), name="dashboard"),
    path('landing/', LandingPageView, name='landing'),
    path('user-list/', UserListView.as_view()),
    path('get-user/', GetUserView, name='get_user'),

    path('tu-modelo/', TuModeloListCreateView, name='TuModeloListCreateView'),
    path('tu-modelo/<int:pk>/', TuModeloRetrieveUpdateDestroyView, name='TuModeloRetrieveUpdateDestroyView'),
    # path('comments/', add_comment, name="add_comment"),
    path('comments/<int:comment_id>/', comment_detail, name="comment_detail"),
    path('tasks_by_user/<int:user_id>/', tasks_by_user, name='tasks_by_user'),
    path('tasks_by_id/<int:task_id>/', tasks_by_id, name='tasks_by_id'),
    path('tasks_by_id/<int:task_id>/comments/', NewPeticionCommentView.as_view(), name='task-comments'),
    path('tasks_by_id/<int:task_id>/comments/<int:comment_id>/', NewPeticionCommentDetailsView.as_view()),
    path('tasks_by_id/<int:task_id>/comments/<int:comment_id>/like/', LikeCommentView.as_view(), name='like-comment'),
    path('tasks/', task_detail, name="tasks_detail"),
    path('imagen/', add_imagen, name="add_imagen"),
    path('tasks/<int:task_id>/', task_detaill, name='task_detaill'),
    path('tasks/<int:task_id>/users_who_liked/', users_who_liked_task, name='users_who_liked_task'),
    path('tasks/<int:task_id>/users_who_liked_task_comment/', users_who_liked_task_comment, name='users_who_liked_task_comment'),
    path('tasksUserSelect/<int:task_id>/', get_task_by_id, name='get_task_by_id'),
    path('traductor/', GetUserView, name=''),
    path('users/', ListUsersView, name='list-users'),
    path('categories/', create_categoryp, name='create-categoryP'),
    path('categories/<int:pk>/', delete_categoryp, name='create-categoryP'),
    path('profiles/<int:profile_id>/like/', like_unlike_profile, name='like-unlike-profile'),
    path('profiles/<int:profile_id>/likes/', list_likes, name='profile-likes'),
    path('new-categories/', new_category_list_create, name='new-categories-list-create'),
    path('new-categories/<int:pk>/', new_category_detail_update_delete, name='new-category-detail-update-delete'),
    path('verify-admin/', verify_admin, name='verify-admin'),
    path('user-details/', get_user_details, name='user-details'),
    path('favoritos/agregar/', agregar_favorito, name='agregar_favorito'),
    path('favoritos/<int:task_id>/eliminar/', eliminar_favorito, name='eliminar_favorito'),
    path('pfavoritos/agregar/', agregar_pfavorito, name='agregar_pfavorito'),
    path('favoritos/listar/', listar_favoritos, name='listar_favoritos'),
    path('pfavoritos/listar/', listar_pfavoritos, name='listar_favoritos'),
    path('pfavoritos/listar/<int:user_id>/', listar_pfavoritos_usuario, name='listar_favoritos_usuario'),
    # path('favoritos/<int:user_id>/', listar_favoritos_usuario, name='listar_favoritos_usuario'),
    path('nuevotasks/<int:task_id>/', nuevo_task_detaill, name='crear-mi-modeloo'),
    path('nuevotasks/', nuevo_task_detail, name="nuevo_tasks_detaill"),
    path('shared-tasks/', create_shared_task, name='create_shared_task'),
    path('shared-tasks/<int:shared_task_id>/', delete_shared_task, name='delete_shared_task'),
    path('postss/', post_list_create, name='post-list-create'),
    path('comments/<int:comment_id>/users_who_liked/', users_who_liked_comment, name='users_who_liked_comment'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('profile/', get_current_user_profile, name='get_current_user_profile'),
    path('portada/', portada_list_create, name='portada-list-create'),
    path('portada/<int:portada_id>/', portada_update_delete, name='portada-update-delete'),
    path('imagen-fija/', imagen_fija_list_create, name='imagen-fija-list-create'),
    path('tasks/<int:task_id>/shared-users/', users_who_shared_task, name='users_who_shared_task'),
    path('usuario/<int:user_id>/portadas/', obtener_portadas_usuario, name='obtener_portadas_usuario'),
    path('usuario/<int:user_id>/imagen-fija/', obtener_imagen_fija_usuario, name='obtener_imagen_fija_usuario'),
    path('favoritos/listar/<int:user_id>/', listar_favoritos_usuario, name='listar_favoritos_usuario'),

    path('agreement/', AgreementView.as_view(), name="agreement"),
    path('exchange/', CurrencyView.as_view(), name="currency"),
    path('directory/', DirectoryView.as_view(), name="directory"),
    path('admin/calendar-events/', AdminCalendarEventView.as_view(), name="adminCalendarEvents"),
    path('admin/calendar-events/<int:pk>', AdminCalendarEventView.as_view(), name="adminCalendarEventsUpdate"),
    path('admin/calendar-categories/', CalendarEventCategoryView.as_view(), name="calendarCategories"),
    path('admin/calendar-categories/<int:pk>', CalendarEventCategoryView.as_view(), name="calendarCategoriesUpdate"),
    path('calendar-event-categories/', UserCalendarEventCategoryView.as_view(), name="userCalendarCategoriesUpdate"),
    path('calendar-events/', UserCalendarEventView.as_view(), name="userCalendarEvents"),
    path('edit-user/', EditUserView),
    path('profileImage/', ProfileImageView),

    # YOI URLS
    path('yoi/', YOI_Homepage.as_view(), name="YOI_Homepage"),
    path('YOI_Assistant/', YOI_AssistantView.as_view(), name="YOI_Assistant"),
    path('YOI_Registration/', YOI_RegistrationView.as_view(), name="YOI_Registration"),
    path('YOI_Registration/<int:pk>', YOI_RegistrationView.as_view(), name="YOI_Registration_Update"),
    path('YOI_Create_Session/', CreateYOICheckoutSession.as_view()),

    # AUTH URLS
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('signup/', SignUpView, name="signup"),
    path('signup/validate-account/', ValidateAccountView, name="validate_account"),
    path('forgot-password/', ForgotPasswordView, name='forgot_password'),
    path('password-reset/', ResetPasswordView, name='password_reset'),

    # ADMIN URLS
    path('admin/users/', AdminUsersView.as_view(), name="admin_users"),
    path('admin/get_users/', AdminUsersView.as_view(), name="AdminUserView"),
    path('admin/get_petition_entries/', AdminPetitionEntriesView.as_view(), name="AdminPetitionEntriesView"),
    path('adminDirectory/', AdminDirectoryView.as_view(), name="adminDirectory"),
    path('admin/', AdminPageView.as_view(), name='admin_page'),
    path('adminExchange/', AdminCurrencyView.as_view(), name="adminCurrency"),
    path('admin/YOI/', YOIAdminView.as_view()),
    
    # BLOG URLS
    path('posts/', PostsView.as_view(), name='post'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('blog/id:<slug>/', BlogDetailView.as_view(), name='blog_details'),
    path('blog_public/', PublicBlogView.as_view(), name='public_blog'),

    # PETITION URLS
    path('petition/representative', RepresentativeSurveyEntryView.as_view(), name="petition"),
    path('petition/do-you-have-a-credencial', CredencialSurveyEntryView.as_view(), name="petition"),
    path('petition/are-you-voting-for-ammon', VotingForAmmonSurveyEntryView.as_view(), name="petition"),
    path('petition/', PetitionView.as_view(), name="petition"),

    # BUSINESS PAGE URLS
    path('businessPage/<slug>/', BusinessPageView.as_view(), name="businessPage"),
    path('businessPostDetails/<slug>/', BusinessPostDetailsView.as_view(), name="businessPostDetails"),
    path('businessPageAdmin/', BusinessPageAdminView.as_view(), name="businessPage"),

    # GROUP URLS
    path('groups/', GroupView.as_view(), name="Groups"),
    path('my_group/', MyGroupView.as_view(), name="MyGroup"),
    path('group_messages/<slug>', GroupMessageView.as_view(), name="GroupMessage"),

    # STRIPE URLS
    path('create-checkout-session/', CreateCheckoutSession.as_view(), name="CreateCheckoutSession"),
    path('subscription/', SubscriptionView.as_view(), name="Subscription"),
    path('create-raffle-checkout-session/', CreateRaffleCheckoutSession.as_view(), name="RaffleCheckoutSession"),
    path('hooks/', StripeWebhooks.as_view(), name="StripeWebhooks"),
 
    #Classifieds
    path('myListings/', MyListingsView.as_view(), name="MyListings"),
    path('listing/items/', ListingsView.as_view(), name="Listings"),
    path('listing/vehicles/', VehicleListingsView.as_view(), name="VehicleListings"),
    path('listing/image-upload/', ListingImageUpload.as_view(), name="ImageUpload"),
    path('listing/favorites/', ClassifiedFavorites.as_view(), name="ClassifiedFavorites"),

    #Raffle
    path('raffle/', RaffleView.as_view()),

    #SendGrid URLS
    path('mail-sender/', MailSenderView, name="mail_sender"),
    
] 

if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

