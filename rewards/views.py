from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Reward, RedeemedReward
from .forms import RewardForm
from core.views import get_partner
from notifications.models import Notification, create_partner_notification

@login_required
def reward_list(request):
    """Display all rewards as a shop, plus a history of redeemed rewards."""
    available_rewards = Reward.objects.filter(is_active=True)
    partner = get_partner(request.user)
    
    # Get all redeemed rewards, ordered by most recent
    all_redeemed_rewards = RedeemedReward.objects.all().order_by('-redeemed_at')

    context = {
        'available_rewards': available_rewards,
        'all_redeemed_rewards': all_redeemed_rewards,
        'user_points': request.user.points,
        'partner': partner,
        'partner_points': partner.points if partner else 0,
    }
    return render(request, 'rewards/list.html', context)

@login_required
def redeem_reward(request, pk):
    """Redeem a reward from the shop."""
    reward_to_redeem = get_object_or_404(Reward, pk=pk, is_active=True)
    user = request.user

    if user.points >= reward_to_redeem.cost:
        user.points -= reward_to_redeem.cost
        user.save()

        RedeemedReward.objects.create(user=user, reward=reward_to_redeem)

        # Notify partner
        create_partner_notification(
            user=request.user,
                message=f'{request.user.username} redeemed a reward: {reward_to_redeem.title}',
                link=reverse('rewards:list')
            )
        
        messages.success(request, _("You have successfully redeemed '{reward}'!").format(reward=reward_to_redeem.title))
    else:
        messages.error(request, _("You don't have enough points to redeem this reward."))
        
    return redirect('rewards:list')

@login_required
def reward_create(request):
    """Create a new reward for the shop."""
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Reward created successfully and added to the shop."))
            return redirect('rewards:list')
    else:
        form = RewardForm()
    
    context = {
        'form': form,
    }
    return render(request, 'rewards/form.html', context)

@login_required
def reward_edit(request, pk):
    """Edit an existing reward."""
    reward = get_object_or_404(Reward, pk=pk)
    
    if request.method == 'POST':
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            messages.success(request, _("Reward updated successfully"))
            return redirect('rewards:list')
    else:
        form = RewardForm(instance=reward)
    
    context = {
        'form': form,
        'reward': reward,
        'is_edit': True,
    }
    return render(request, 'rewards/form.html', context)

@login_required
def reward_delete(request, pk):
    """Delete a reward."""
    reward = get_object_or_404(Reward, pk=pk)
    
    if request.method == 'POST':
        reward.delete()
        messages.success(request, _("Reward deleted successfully"))
        return redirect('rewards:list')
    
    context = {
        'reward': reward,
    }
    return render(request, 'rewards/delete.html', context)
