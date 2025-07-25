from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('read/all/', views.mark_all_as_read, name='mark_all_as_read'),
    path('test-webhook/', views.test_webhook, name='test_webhook'),
    path('webhook-status/', views.check_webhook_status, name='webhook_status'),
]
