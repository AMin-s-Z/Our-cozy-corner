from django.contrib import admin
from .models import Reward, RedeemedReward

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'cost', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('cost', 'is_active')
    ordering = ('-created_at',)

@admin.register(RedeemedReward)
class RedeemedRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'redeemed_at')
    list_filter = ('reward',)
    search_fields = ('user__username', 'reward__title')
    readonly_fields = ('user', 'reward', 'redeemed_at')
    ordering = ('-redeemed_at',)

    def has_add_permission(self, request):
        return False