from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class RewardCategory(models.Model):
    """Categories for rewards such as 'Date Night', 'Gift', etc."""
    name = models.CharField(_("نام دسته‌بندی"), max_length=100)
    icon = models.CharField(_("کلاس آیکون"), max_length=50, help_text=_("نام کلاس آیکون بوت‌استرپ (مثال: 'bi-heart')"))
    
    class Meta:
        verbose_name = _("دسته‌بندی جایزه")
        verbose_name_plural = _("دسته‌بندی‌های جوایز")
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Reward(models.Model):
    """A template for a reward that can be purchased in the shop."""
    title = models.CharField(_("عنوان جایزه"), max_length=200)
    description = models.TextField(_("توضیحات"), blank=True)
    cost = models.PositiveIntegerField(_("امتیاز مورد نیاز"), default=0)
    category = models.ForeignKey(
        RewardCategory,
        on_delete=models.SET_NULL,
        related_name='rewards',
        verbose_name=_("دسته‌بندی"),
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_("فعال"), default=True, help_text=_("فقط جوایز فعال در فروشگاه نمایش داده می‌شوند."))
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("قالب جایزه")
        verbose_name_plural = _("قالب‌های جوایز")
        ordering = ['cost']
    
    def __str__(self):
        return self.title

class RedeemedReward(models.Model):
    """A record of a user redeeming a reward from the shop."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='redeemed_rewards',
        verbose_name=_("کاربر")
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name='redemptions',
        verbose_name=_("جایزه")
    )
    redeemed_at = models.DateTimeField(_("تاریخ دریافت"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("جایزه دریافت شده")
        verbose_name_plural = _("جوایز دریافت شده")
        ordering = ['-redeemed_at']
        
    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.title}"