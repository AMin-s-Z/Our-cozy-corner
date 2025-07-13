from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.urls import reverse

from .models import Goal
from .forms import GoalForm
from core.views import get_partner
from notifications.models import Notification, create_partner_notification

@login_required
def goal_list(request):
    """Display list of all goals."""
    # Show goals from both the user and their partner
    goals = Goal.objects.filter(
        created_by__in=[request.user, get_partner(request.user)]
    ).order_by('-priority', 'deadline')
    
    # Separate active and completed goals
    active_goals = goals.filter(completed=False)
    completed_goals = goals.filter(completed=True)
    
    return render(request, 'goals/list.html', {
        'active_goals': active_goals,
        'completed_goals': completed_goals
    })

@login_required
def goal_detail(request, pk):
    """Display details of a specific goal."""
    goal = get_object_or_404(
        Goal, 
        pk=pk,
        created_by__in=[request.user, get_partner(request.user)]
    )
    
    return render(request, 'goals/detail.html', {'goal': goal})

@login_required
def goal_create(request):
    """Create a new goal."""
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = request.user
            goal.save()

            # Notify partner
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} created a new goal: {goal.title}',
                link=reverse('goals:detail', kwargs={'pk': goal.pk})
            )

            messages.success(request, _('Goal created successfully.'))
            return redirect('goals:detail', pk=goal.pk)
    else:
        form = GoalForm()
    
    return render(request, 'goals/form.html', {
        'form': form,
        'title': _('Create Goal')
    })

@login_required
def goal_edit(request, pk):
    """Edit an existing goal."""
    goal = get_object_or_404(Goal, pk=pk, created_by__in=[request.user, get_partner(request.user)])
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()

            # Notify the other user
            if request.user == goal.created_by:
                # If the creator edited the goal, notify the partner
                create_partner_notification(
                    user=request.user,
                    message=f'{request.user.username} edited the goal: {goal.title}',
                    link=reverse('goals:detail', kwargs={'pk': goal.pk})
                )
            else:
                # If the partner edited the goal, notify the creator
                Notification.objects.create(
                    recipient=goal.created_by,
                    message=f'{request.user.username} edited the goal: {goal.title}',
                    link=reverse('goals:detail', kwargs={'pk': goal.pk})
                )

            messages.success(request, _('Goal updated successfully.'))
            return redirect('goals:detail', pk=goal.pk)
    else:
        form = GoalForm(instance=goal)
    
    return render(request, 'goals/form.html', {
        'form': form,
        'goal': goal,
        'title': _('Edit Goal')
    })

@login_required
def goal_delete(request, pk):
    """Delete an existing goal."""
    goal = get_object_or_404(Goal, pk=pk, created_by__in=[request.user, get_partner(request.user)])
    
    if request.method == 'POST':
        
        # Notify the other user
        if request.user == goal.created_by:
            # If the creator deleted the goal, notify the partner
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} deleted the goal: {goal.title}',
                link=reverse('goals:list')
            )
        else:
            # If the partner deleted the goal, notify the creator
            Notification.objects.create(
                recipient=goal.created_by,
                message=f'{request.user.username} deleted the goal: {goal.title}',
                link=reverse('goals:list')
            )

        goal.delete()
        messages.success(request, _('Goal deleted successfully.'))
        return redirect('goals:list')
    
    return render(request, 'goals/delete.html', {'goal': goal})

@login_required
def goal_toggle_complete(request, pk):
    """Toggle the completion status of a goal."""
    goal = get_object_or_404(Goal, pk=pk, created_by__in=[request.user, get_partner(request.user)])
    
    goal.completed = not goal.completed
    if goal.completed:
        goal.progress = 100
    else:
        goal.progress = 0
    
    goal.save()

    # Notify the other user
    if goal.completed:
        if request.user == goal.created_by:
            # If the creator completed the goal, notify the partner
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} completed the goal: {goal.title}',
                link=reverse('goals:detail', kwargs={'pk': goal.pk})
            )
        else:
            # If the partner completed the goal, notify the creator
            Notification.objects.create(
                recipient=goal.created_by,
                message=f'{request.user.username} completed the goal: {goal.title}',
                link=reverse('goals:detail', kwargs={'pk': goal.pk})
            )
    
    messages.success(
        request,
        _('Goal marked as completed.') if goal.completed else _('Goal marked as active.')
    )
    return redirect('goals:detail', pk=goal.pk)

@login_required
def goal_update_progress(request, pk):
    """Update the progress of a goal via AJAX."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        goal = get_object_or_404(Goal, pk=pk, created_by__in=[request.user, get_partner(request.user)])
        
        try:
            progress = int(request.POST.get('progress', 0))
            
            if 0 <= progress <= 100:
                goal.progress = progress
                
                # If progress is 100%, mark the goal as completed
                if progress == 100 and not goal.completed:
                    goal.completed = True
                    
                    # Notify the other user
                    if request.user == goal.created_by:
                        # If the creator completed the goal, notify the partner
                        create_partner_notification(
                            user=request.user,
                            message=f'{request.user.username} completed the goal: {goal.title}',
                            link=reverse('goals:detail', kwargs={'pk': goal.pk})
                        )
                    else:
                        # If the partner completed the goal, notify the creator
                        Notification.objects.create(
                            recipient=goal.created_by,
                            message=f'{request.user.username} completed the goal: {goal.title}',
                            link=reverse('goals:detail', kwargs={'pk': goal.pk})
                        )

                elif progress < 100 and goal.completed:
                    goal.completed = False

                goal.save()
                
                return JsonResponse({'success': True, 'progress': goal.progress, 'completed': goal.completed})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid progress value.'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid progress value.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

