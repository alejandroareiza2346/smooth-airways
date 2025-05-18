from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import uuid

class User(AbstractUser):
    MEMBERSHIP_TIERS = [
        ('STANDARD', 'Standard'),
        ('ELITE', 'Elite'),
        ('ULTRA', 'Ultra'),
        ('CORPORATE', 'Corporate'),
    ]

    class Role(models.TextChoices):
        CLIENT = 'CLIENT', _('Cliente')
        VIP = 'VIP', _('VIP')
        STAFF = 'STAFF', _('Staff')
        SUPERADMIN = 'SUPERADMIN', _('Superadministrador')

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.CLIENT
    )
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    membership_tier = models.CharField(max_length=20, choices=MEMBERSHIP_TIERS, default='STANDARD')
    membership_number = models.CharField(max_length=10, unique=True, blank=True)
    membership_start_date = models.DateField(null=True, blank=True)
    membership_end_date = models.DateField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    passport_number = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    preferred_language = models.CharField(max_length=10, default='es')
    dietary_preferences = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    company_position = models.CharField(max_length=100, blank=True)
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    # Preferences
    preferred_aircraft_type = models.CharField(max_length=100, blank=True)
    preferred_seat_type = models.CharField(max_length=50, blank=True)
    preferred_meal_type = models.CharField(max_length=50, blank=True)
    
    # Override the groups field
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    # Override the user_permissions field
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        if not self.membership_number:
            self.membership_number = f'SM{str(uuid.uuid4())[:6].upper()}'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_premium(self):
        return self.membership_tier in ['ELITE', 'ULTRA', 'CORPORATE']

    def is_client(self):
        return self.role == self.Role.CLIENT

    def is_vip(self):
        return self.role == self.Role.VIP

    def is_staff_member(self):
        return self.role == self.Role.STAFF

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return timezone.now() <= self.expires_at

    class Meta:
        verbose_name = _('password reset token')
        verbose_name_plural = _('password reset tokens')