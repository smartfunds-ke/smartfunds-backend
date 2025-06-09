from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from .managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User model with role-based authentication
    """
    class UserRole(models.TextChoices):
        CITIZEN = 'citizen', 'Citizen'
        FUND_OFFICER = 'fund_officer', 'Fund Officer'
        FUND_ADMIN = 'fund_admin', 'Fund Admin'
        SUPERADMIN = 'superadmin', 'Super Admin'

    # Override email to be unique and required
    email = models.EmailField(unique=True, blank=False, null=False)

    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        help_text="Required for USSD/SMS access"
    )

    # Role and access method
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CITIZEN,
        db_index=True
    )

    # Additional fields
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_method = models.CharField(max_length=20, blank=True)

    # User manager
    objects = CustomUserManager()

    # Use email as username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def full_name(self):
        """
        Return full name of user
        """
        return f"{self.first_name} {self.last_name}".strip()

    def is_admin_user(self):
        """Check if user has admin privileges"""
        return self.role in [
            self.UserRole.FUND_ADMIN,
            self.UserRole.SUPERADMIN
        ]

    def can_review_applications(self):
        """Check if user can review fund applications"""
        return self.role in [
            self.UserRole.FUND_OFFICER,
            self.UserRole.FUND_ADMIN,
            self.UserRole.SUPERADMIN
        ]

    def can_deploy_contracts(self):
        """Check if user can deploy smart contracts"""
        return self.role in [
            self.UserRole.FUND_ADMIN,
            self.UserRole.SUPERADMIN
        ]


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)

    # Notification/USSD specific settings
    preferred_language = models.CharField(max_length=10, default='en')
    sms_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    ussd_session_timeout = models.IntegerField(default=300)  # seconds

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_user_profile'

    def __str__(self):
        return f"{self.user.email} Profile"


class LoginAttempt(models.Model):
    """
    Track login attempts for security
    """
    class LoginMethod(models.TextChoices):
        USSD = 'ussd', 'USSD'
        SMS = 'sms', 'SMS'
        WEB = 'web', 'Web'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    method = models.CharField(max_length=10, choices=LoginMethod.choices)
    successful = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'accounts_login_attempt'
        ordering = ['-timestamp']

    def __str__(self):
        status = "Successful" if self.successful else "Failed"
        return f"{self.email} - {status} ({self.method})"
