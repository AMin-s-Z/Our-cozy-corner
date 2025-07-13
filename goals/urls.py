from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.goal_list, name='list'),
    path('create/', views.goal_create, name='create'),
    path('<int:pk>/', views.goal_detail, name='detail'),
    path('<int:pk>/edit/', views.goal_edit, name='edit'),
    path('<int:pk>/delete/', views.goal_delete, name='delete'),
    path('<int:pk>/toggle-complete/', views.goal_toggle_complete, name='toggle_complete'),
    path('<int:pk>/update-progress/', views.goal_update_progress, name='update_progress'),
] 