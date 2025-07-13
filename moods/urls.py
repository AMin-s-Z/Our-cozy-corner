from django.urls import path
from . import views

app_name = 'moods'

urlpatterns = [
    path('', views.mood_list, name='list'),
    path('create/', views.mood_create, name='create'),
    path('<int:pk>/', views.mood_detail, name='detail'),
    path('<int:pk>/update/', views.mood_update, name='update'),
    path('<int:pk>/delete/', views.mood_delete, name='delete'),
] 