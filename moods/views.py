from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Avg
from django.urls import reverse
import json
import datetime

from .models import Mood
from .forms import MoodForm
from core.views import get_partner
from notifications.models import Notification, create_partner_notification

@login_required
def mood_list(request):
    """Display list of all mood entries."""
    # Get moods from both the user and their partner
    moods = Mood.objects.filter(
        user__in=[request.user, get_partner(request.user)]
    ).order_by('-date', '-created_at')
    
    # Calculate average mood ratings
    user_avg_rating = Mood.objects.filter(user=request.user).aggregate(avg=Avg('rating'))['avg'] or 0
    partner = get_partner(request.user)
    partner_avg_rating = 0
    if partner:
        partner_avg_rating = Mood.objects.filter(user=partner).aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Get data for mood chart
    last_30_days = timezone.now().date() - datetime.timedelta(days=30)
    user_moods = Mood.objects.filter(user=request.user, date__gte=last_30_days).order_by('date')
    
    mood_dates = []
    mood_ratings = []
    
    for mood in user_moods:
        mood_dates.append(mood.date.strftime('%m/%d'))
        mood_ratings.append(mood.rating)
    
    context = {
        'moods': moods,
        'user_avg_rating': round(user_avg_rating, 1),
        'partner_avg_rating': round(partner_avg_rating, 1),
        'mood_dates': json.dumps(mood_dates),
        'mood_ratings': json.dumps(mood_ratings),
    }
    
    return render(request, 'moods/list.html', context)

@login_required
def mood_create(request):
    """Create a new mood entry."""
    # Check if user already entered a mood for today
    today = timezone.now().date()
    existing_mood = Mood.objects.filter(user=request.user, date=today).first()
    
    if existing_mood:
        messages.warning(request, _('شما قبلاً حال و هوای امروز خود را ثبت کرده‌اید.'))
        return redirect('moods:update', pk=existing_mood.pk)
    
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            mood = form.save(commit=False)
            mood.user = request.user
            mood.save()

            # Notify partner
            create_partner_notification(
                user=request.user,
                    message=f'{request.user.username} has set their mood for today.',
                    link=reverse('moods:detail', kwargs={'pk': mood.pk})
                )

            messages.success(request, _('حال و هوای شما با موفقیت ثبت شد.'))
            return redirect('moods:list')
    else:
        form = MoodForm()
    
    return render(request, 'moods/form.html', {
        'form': form,
        'title': _('ثبت حال و هوای امروز')
    })

@login_required
def mood_update(request, pk):
    """Update an existing mood entry."""
    mood = get_object_or_404(Mood, pk=pk, user__in=[request.user, get_partner(request.user)])
    
    if request.method == 'POST':
        form = MoodForm(request.POST, instance=mood)
        if form.is_valid():
            form.save()

            # Notify the other user
            if request.user == mood.user:
                # If the creator edited the mood, notify the partner
                create_partner_notification(
                    user=request.user,
                    message=f'{request.user.username} updated their mood.',
                    link=reverse('moods:detail', kwargs={'pk': mood.pk})
                )
            else:
                # If the partner edited the mood, notify the creator
                Notification.objects.create(
                    recipient=mood.user,
                    message=f'{request.user.username} updated their mood.',
                    link=reverse('moods:detail', kwargs={'pk': mood.pk})
                )

            messages.success(request, _('حال و هوای شما با موفقیت به‌روزرسانی شد.'))
            return redirect('moods:list')
    else:
        form = MoodForm(instance=mood)
    
    return render(request, 'moods/form.html', {
        'form': form,
        'mood': mood,
        'title': _('ویرایش حال و هوا')
    })

@login_required
def mood_delete(request, pk):
    """Delete a mood entry."""
    mood = get_object_or_404(Mood, pk=pk, user__in=[request.user, get_partner(request.user)])
    
    if request.method == 'POST':
        
        # Notify the other user
        if request.user == mood.user:
            # If the creator deleted the mood, notify the partner
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} deleted their mood entry.',
                link=reverse('moods:list')
            )
        else:
            # If the partner deleted the mood, notify the creator
            Notification.objects.create(
                recipient=mood.user,
                message=f'{request.user.username} deleted their mood entry.',
                link=reverse('moods:list')
            )

        mood.delete()
        messages.success(request, _('حال و هوای شما با موفقیت حذف شد.'))
        return redirect('moods:list')
    
    return render(request, 'moods/delete.html', {'mood': mood})

@login_required
def mood_detail(request, pk):
    """View details of a specific mood entry."""
    mood = get_object_or_404(Mood, pk=pk, user__in=[request.user, get_partner(request.user)])
    
    return render(request, 'moods/detail.html', {'mood': mood})

