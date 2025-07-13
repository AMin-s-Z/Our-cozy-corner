from django.urls import path
from . import views

app_name = 'memories'

urlpatterns = [
    path('', views.memory_list, name='list'),
    path('create/', views.memory_create, name='create'),
    path('<int:pk>/', views.memory_detail, name='detail'),
    path('<int:pk>/edit/', views.memory_edit, name='edit'),
    path('<int:pk>/delete/', views.memory_delete, name='delete'),
    path('search/', views.memory_search, name='search'),
    path('image/<int:pk>/delete/', views.memory_image_delete, name='image_delete'),
] 