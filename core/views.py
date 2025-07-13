from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import logout
import json

from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from notifications.models import Notification

def index(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/index.html')

def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Check if max users reached
    if User.objects.count() >= settings.MAX_USERS:
        messages.error(request, _("Maximum number of users reached. Registration is closed."))
        return redirect('login')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _("Registration successful. You can now log in."))
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})

def get_partner(user):
    """Get the partner of the current user."""
    if user.partner_type == 'partner1':
        return User.objects.filter(partner_type='partner2').first()
    else:
        return User.objects.filter(partner_type='partner1').first()

def custom_logout(request):
    """Custom logout view to handle both GET and POST requests."""
    logout(request)
    messages.success(request, _("You have been successfully logged out."))
    return redirect('login')

@login_required
def dashboard(request):
    """Main dashboard view after login."""
    # Import here to avoid circular imports
    from memories.models import Memory
    from goals.models import Goal
    from moods.models import Mood
    from rewards.models import Reward
    
    # Get recent memories
    recent_memories = Memory.objects.filter(
        user__in=[request.user, get_partner(request.user)]
    ).order_by('-created_at')[:4]
    
    # Get active goals
    active_goals = Goal.objects.filter(
        completed=False
    ).order_by('deadline')[:4]
    
    # Get mood data for chart
    recent_moods = Mood.objects.filter(
        user=request.user
    ).order_by('-date')[:7]
    
    mood_labels = []
    mood_values = []
    
    if recent_moods:
        # Reverse to get chronological order
        for mood in reversed(list(recent_moods)):
            mood_labels.append(mood.date.strftime('%m/%d'))
            mood_values.append(mood.rating)
    
    # Get available rewards count is no longer needed as it's a shop now
    
    context = {
        'recent_memories': recent_memories,
        'active_goals': active_goals,
        'mood_data': bool(recent_moods),
        'mood_labels': json.dumps(mood_labels),
        'mood_values': json.dumps(mood_values),
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    """User profile view and edit."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()

            # Notify partner
            from notifications.models import create_partner_notification
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} updated their profile.',
                link=reverse('profile')
            )

            messages.success(request, _("Profile updated successfully."))
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/profile.html', {'form': form})

def manifest(request):
    """Return the PWA manifest file."""
    return JsonResponse(
        {
            "name": settings.PWA_APP_NAME,
            "short_name": settings.PWA_APP_NAME,
            "description": settings.PWA_APP_DESCRIPTION,
            "start_url": "/",
            "display": "standalone",
            "background_color": settings.PWA_APP_BACKGROUND_COLOR,
            "theme_color": settings.PWA_APP_THEME_COLOR,
            "icons": settings.PWA_APP_ICONS,
        }
    )

def service_worker(request):
    """Return the service worker JavaScript."""
    try:
        # Use the correct path to the service worker file
        with open("static/js/service-worker.js", 'r', encoding='utf-8') as f:
            content = f.read()
        response = HttpResponse(content, content_type="application/javascript")
        # Add cache control headers to prevent caching issues
        response['Service-Worker-Allowed'] = '/'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except Exception as e:
        # Return a simple service worker if the file can't be read
        content = """
        // Simple service worker
        self.addEventListener('install', function(event) {
            self.skipWaiting();
        });

        self.addEventListener('activate', function(event) {
            return self.clients.claim();
        });

        self.addEventListener('fetch', function(event) {
            event.respondWith(fetch(event.request));
        });
        """
        response = HttpResponse(content, content_type="application/javascript")
        response['Service-Worker-Allowed'] = '/'
        return response

def offline(request):
    """Offline page view."""
    return render(request, 'core/offline.html')