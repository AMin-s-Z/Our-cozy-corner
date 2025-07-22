from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Reward(models.Model):
    """A template for a reward that can be purchased in the shop."""
    title = models.CharField(_("عنوان جایزه"), max_length=200)
    description = models.TextField(_("توضیحات"), blank=True)
    cost = models.PositiveIntegerField(_("امتیاز مورد نیاز"), default=0)
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