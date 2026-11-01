"""
Accounts models for FixSoftRepair
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model extending AbstractUser with role-based access control"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        TECHNICIAN = 'TECHNICIAN', _('Technician')
        CASHIER = 'CASHIER', _('Cashier')
    
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=Role.choices,
        default=Role.TECHNICIAN
    )
    
    telephone = models.CharField(
        _('Telephone'),
        max_length=20,
        blank=True,
        null=True
    )
    
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        _('Active'),
        default=True
    )
    
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add=True
    )
    
    date_updated = models.DateTimeField(
        _('Date Updated'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name if self.first_name else self.username
    
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN
    
    def is_cashier(self):
        return self.role == self.Role.CASHIER
    
    def has_perm(self, perm, obj=None):
        """Override permission check based on role"""
        if self.is_admin():
            return True
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """Override module permission check based on role"""
        if self.is_admin():
            return True
        return super().has_module_perms(app_label)
