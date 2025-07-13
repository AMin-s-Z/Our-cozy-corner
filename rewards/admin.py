from django.contrib import admin
from .models import Reward, RewardCategory, RedeemedReward

@admin.register(RewardCategory)
class RewardCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'cost', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category')
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