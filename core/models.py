from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model for our application.
    Limited to only two users - the couple.
    """
    PARTNER_CHOICES = [
        ('partner1', 'Partner 1'),
        ('partner2', 'Partner 2'),
    ]
    
    partner_type = models.CharField(
        max_length=10,
        choices=PARTNER_CHOICES,
        default='partner1',
        verbose_name=_("Partner Type")
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        verbose_name=_("Profile Picture")
    )
    
    points = models.PositiveIntegerField(default=0, verbose_name=_("Reward Points"))
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
    
    def __str__(self):
        return self.username 