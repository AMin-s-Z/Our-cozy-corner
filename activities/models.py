from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Activity(models.Model):
    """A predefined activity that users can complete to earn points."""
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    points = models.PositiveIntegerField(_("Points"), help_text=_(""))
    is_active = models.BooleanField(_("Active"), default=True, help_text=_(""))

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ['-points']

    def __str__(self):
        return self.title

class CompletedActivity(models.Model):
    """A record of a user completing an activity."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='completed_activities',
        verbose_name=_("User")
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name=_("Activity")
    )
    completed_at = models.DateTimeField(_("Completed At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Completed Activity")
        verbose_name_plural = _("Completed Activities")
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} completed {self.activity.title}"