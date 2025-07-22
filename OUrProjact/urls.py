"""
URL configuration for OUrProjact project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from django.views.generic import RedirectView
from django.http import JsonResponse

# Handler for Chrome DevTools requests
def chrome_devtools_handler(request):
    return JsonResponse({})

urlpatterns = [
    path("admin/", admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("", include("core.urls")),
    path("memories/", include("memories.urls")),
    path("goals/", include("goals.urls")),
    path("moods/", include("moods.urls")),
    path("rewards/", include("rewards.urls")),
    path("activities/", include("activities.urls")),
    path("notifications/", include("notifications.urls")),
    
    # PWA URLs
    path('manifest.json', core_views.manifest, name='manifest'),
    path('sw.js', core_views.service_worker, name='service_worker'),
    path('offline/', core_views.offline, name='offline'),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/images/icons/icon-192x192.svg', permanent=True)),
    
    # Chrome DevTools
    re_path(r'^\.well-known/appspecific/.*', chrome_devtools_handler),
]

# Add media file serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
