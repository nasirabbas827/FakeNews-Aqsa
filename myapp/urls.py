from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('news-history/', views.news_history_view, name='news_history'),    
    path('news-history/export-csv/', views.export_news_history_csv, name='export_news_csv'),
     path('datasets/', views.dataset_list_view, name='dataset_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
