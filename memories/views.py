from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.urls import reverse

from .models import Memory
from .forms import MemoryForm
from core.views import get_partner
from notifications.models import Notification, create_partner_notification

@login_required
def memory_list(request):
    """Display list of all memories."""
    # Get memories from both the user and their partner
    memories = Memory.objects.filter(
        user__in=[request.user, get_partner(request.user)]
    ).order_by('-date', '-created_at')
    
    return render(request, 'memories/list.html', {'memories': memories})

@login_required
def memory_detail(request, pk):
    """Display details of a specific memory."""
    memory = get_object_or_404(
        Memory, 
        pk=pk, 
        user__in=[request.user, get_partner(request.user)]
    )
    
    return render(request, 'memories/detail.html', {'memory': memory})

@login_required
def memory_create(request):
    """Create a new memory."""
    if request.method == 'POST':
        form = MemoryForm(request.POST, request.FILES)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.user = request.user
            memory.save()

            # Notify partner
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} created a new memory: {memory.title}',
                link=reverse('memories:detail', kwargs={'pk': memory.pk})
            )

            messages.success(request, _('Memory created successfully.'))
            return redirect('memories:detail', pk=memory.pk)
    else:
        form = MemoryForm()
    
    return render(request, 'memories/form.html', {
        'form': form,
        'title': _('Create Memory')
    })

@login_required
def memory_edit(request, pk):
    """Edit an existing memory."""
    memory = get_object_or_404(Memory, pk=pk, user__in=[request.user, get_partner(request.user)])
    
    if request.method == 'POST':
        form = MemoryForm(request.POST, request.FILES, instance=memory)
        if form.is_valid():
            form.save()

            # Notify the other user
            if request.user == memory.user:
                # If the creator edited the memory, notify the partner
                create_partner_notification(
                    user=request.user,
                    message=f'{request.user.username} edited the memory: {memory.title}',
                    link=reverse('memories:detail', kwargs={'pk': memory.pk})
                )
            else:
                # If the partner edited the memory, notify the creator
                Notification.objects.create(
                    recipient=memory.user,
                    message=f'{request.user.username} edited the memory: {memory.title}',
                    link=reverse('memories:detail', kwargs={'pk': memory.pk})
                )

            messages.success(request, _('Memory updated successfully.'))
            return redirect('memories:detail', pk=memory.pk)
    else:
        form = MemoryForm(instance=memory)
    
    return render(request, 'memories/form.html', {
        'form': form,
        'memory': memory,
        'title': _('Edit Memory')
    })

@login_required
def memory_delete(request, pk):
    """Delete an existing memory."""
    memory = get_object_or_404(Memory, pk=pk, user__in=[request.user, get_partner(request.user)])
    
    if request.method == 'POST':
        
        # Notify the other user
        if request.user == memory.user:
            # If the creator deleted the memory, notify the partner
            create_partner_notification(
                user=request.user,
                message=f'{request.user.username} deleted the memory: {memory.title}',
                link=reverse('memories:list')
            )
        else:
            # If the partner deleted the memory, notify the creator
            Notification.objects.create(
                recipient=memory.user,
                message=f'{request.user.username} deleted the memory: {memory.title}',
                link=reverse('memories:list')
            )

        memory.delete()
        messages.success(request, _('Memory deleted successfully.'))
        return redirect('memories:list')
    
    return render(request, 'memories/delete.html', {'memory': memory})

@login_required
def memory_search(request):
    """Search memories."""
    query = request.GET.get('q', '')
    
    if query:
        memories = Memory.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(location__icontains=query),
            user__in=[request.user, get_partner(request.user)]
        ).order_by('-date', '-created_at')
    else:
        memories = Memory.objects.none()
    
    return render(request, 'memories/search.html', {
        'memories': memories, 
        'query': query
    })
