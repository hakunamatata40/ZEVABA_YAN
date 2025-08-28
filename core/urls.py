from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import PublicationSitemap, ClubSitemap, ChallengeSitemap, PageSitemap

sitemaps = {
    'publications': PublicationSitemap,
    'clubs': ClubSitemap,
    'challenges': ChallengeSitemap,
    'pages': PageSitemap,
}
  
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('feed/', views.feed, name='feed'),
    path('update_profile_picture/', views.update_profile_picture, name='update_profile_picture'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('personalized_feed/', views.personalized_feed, name='personalized_feed'),
    path('publication/create/', views.publication_create, name='publication_create'),
    path('react/<int:pk>/', views.react, name='react'),
    path('like_dislike/<int:pk>/', views.like_dislike, name='like_dislike'),
    path('clubs/', views.clubs, name='clubs'),
    path('club/<int:pk>/', views.club_detail, name='club_detail'),
    path('club/<int:pk>/subscribe/', views.club_subscribe, name='club_subscribe'),
    path('club/<int:pk>/unsubscribe/', views.club_unsubscribe, name='club_unsubscribe'),
    path('club/<int:pk>/manage_admins/', views.club_manage_admins, name='club_manage_admins'),
    path('club/<int:pk>/messages/', views.club_messages, name='club_messages'),
    path('club/<int:pk>/message/reply/', views.reply_to_club_message, name='reply_to_club_message'),
    path('report_user/<int:pk>/', views.report_user, name='report_user'),
    path('search/', views.search, name='search'),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('message/<int:pk>/', views.send_message, name='send_message'),
    path('messages/', views.messages, name='messages'),
    path('search_messages/', views.search_messages, name='search_messages'),
    path('club/<int:pk>/messages/', views.club_messages, name='club_messages'),
    path('challenges/', views.challenges, name='challenges'),
    
    # path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('mentorship/', views.mentorship, name='mentorship'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('history/', views.history, name='history'),
    path('settings/', views.settings, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('help/', views.help, name='help'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('club/create/', views.club_create, name='club_create'),
    path('page/create/', views.page_create, name='page_create'),
    path('page/<int:pk>/', views.page_detail, name='page_detail'),
    path('club/<int:pk>/edit/', views.club_edit, name='club_edit'),
    path('club/<int:pk>/delete/', views.club_delete, name='club_delete'),
    path('page/<int:pk>/edit/', views.page_edit, name='page_edit'),
    path('page/<int:pk>/delete/', views.page_delete, name='page_delete'),
    path('page/<int:pk>/subscribe/', views.page_subscribe, name='page_subscribe'),
    path('page/<int:pk>/unsubscribe/', views.page_unsubscribe, name='page_unsubscribe'),
    path('publication/<int:pk>/edit/', views.publication_edit, name='publication_edit'),
    path('reaction/<int:reaction_id>/reply/', views.reply, name='reply'),
    path('publication/<int:pk>/', views.PublicationDetailView.as_view(), name='publication_detail'),
    path('club/<int:pk>/', views.ClubDetailView.as_view(), name='club_detail'),
    path('challenge/<int:pk>/', views.ChallengeDetailView.as_view(), name='challenge_detail'),
    path('subscribe/<int:account_id>/', views.subscribe, name='subscribe'),
    path('unsubscribe/<int:account_id>/', views.unsubscribe, name='unsubscribe'),
    path('page/<int:pk>/', views.PageDetailView.as_view(), name='page_detail'),

    # Utilisez un chemin différent pour éviter le conflit
    path('profile-edit/details/', views.profile_details, name='profile_details'),
    path('profile-edit/school/remove/<int:index>/', views.remove_school, name='remove_school'),
    path('profile-edit/hobby/remove/<int:index>/', views.remove_hobby, name='remove_hobby'),
    
    path('profile/<str:username>/', views.profile, name='profile'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)