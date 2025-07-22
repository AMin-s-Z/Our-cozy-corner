from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.activity_list, name='list'),
    path('create/', views.activity_create, name='create'),
    path('complete/<int:pk>/', views.complete_activity, name='complete'),
]
