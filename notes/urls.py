from django.urls import path, re_path
from . import views

app_name = 'notes'

urlpatterns = [
    # Note views
    path('', views.note_list, name='list'),
    path('create/', views.note_create, name='create'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/$', views.note_detail, name='detail'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/update/$', views.note_update, name='update'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/delete/$', views.note_delete, name='delete'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/pin/$', views.toggle_pin, name='toggle_pin'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/reminded/$', views.mark_reminded, name='mark_reminded'),
    
    # Attachment views
    path('attachment/<int:pk>/delete/', views.attachment_delete, name='attachment_delete'),
    
    # Category views
    path('categories/', views.category_list, name='category_list'),
    re_path(r'^categories/(?P<slug>[-\w\u0600-\u06FF]+)/$', views.notes_by_category, name='category_detail'),
    re_path(r'^categories/(?P<slug>[-\w\u0600-\u06FF]+)/update/$', views.category_update, name='category_update'),
    re_path(r'^categories/(?P<slug>[-\w\u0600-\u06FF]+)/delete/$', views.category_delete, name='category_delete'),
    
    # Tag views
    path('tags/', views.tag_list, name='tag_list'),
    re_path(r'^tags/(?P<slug>[-\w\u0600-\u06FF]+)/$', views.notes_by_tag, name='tag_detail'),
    re_path(r'^tags/(?P<slug>[-\w\u0600-\u06FF]+)/update/$', views.tag_update, name='tag_update'),
    re_path(r'^tags/(?P<slug>[-\w\u0600-\u06FF]+)/delete/$', views.tag_delete, name='tag_delete'),
    
    # Special views
    path('reminders/', views.reminders, name='reminders'),
] 