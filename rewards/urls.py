from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('', views.reward_list, name='list'),
    path('create/', views.reward_create, name='create'),
    path('edit/<int:pk>/', views.reward_edit, name='edit'),
    path('delete/<int:pk>/', views.reward_delete, name='delete'),
    path('redeem/<int:pk>/', views.redeem_reward, name='redeem'),
]