from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Activity, CompletedActivity
from django.db.models import Count
from core.views import get_partner
from notifications.models import Notification, create_partner_notification

@login_required
def activity_list(request):
    """Displays a list of all available activities and how many times the user and their partner have completed them."""
    all_activities = Activity.objects.filter(is_active=True)
    partner = get_partner(request.user)

    # Get a count of completions for each activity by the current user
    user_completed_counts = CompletedActivity.objects.filter(
        user=request.user
    ).values(
        'activity__pk'
    ).annotate(
        count=Count('id')
    ).values('activity__pk', 'count')
    user_completion_map = {item['activity__pk']: item['count'] for item in user_completed_counts}

    # Get a count of completions for each activity by the partner
    partner_completion_map = {}
    if partner:
        partner_completed_counts = CompletedActivity.objects.filter(
            user=partner
        ).values(
            'activity__pk'
        ).annotate(
            count=Count('id')
        ).values('activity__pk', 'count')
        partner_completion_map = {item['activity__pk']: item['count'] for item in partner_completed_counts}

    activities = []
    for activity in all_activities:
        activities.append({
            'activity': activity,
            'user_completions': user_completion_map.get(activity.pk, 0),
            'partner_completions': partner_completion_map.get(activity.pk, 0)
        })
        
    context = {
        'activities': activities,
        'partner': partner,
    }
    return render(request, 'activities/list.html', context)

@login_required
def complete_activity(request, pk):
    """Marks an activity as complete for the current user and awards points."""
    activity = get_object_or_404(Activity, pk=pk, is_active=True)
    
    # The check for previous completion is removed to allow multiple completions.
    
    # Award points and create a completion record
    request.user.points += activity.points
    request.user.save()
    
    CompletedActivity.objects.create(user=request.user, activity=activity)

    # Notify partner
    create_partner_notification(
        user=request.user,
            message=f'{request.user.username} completed the activity: {activity.title}',
            link=reverse('activities:list')
        )
    
    messages.success(request, _("Congratulations! You have completed '{activity}' and earned {points} points.").format(activity=activity.title, points=activity.points))
    return redirect('activities:list')
