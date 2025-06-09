from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')

        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superadmin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Allow authentication with email
        """
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})

    def citizens(self):
        """Get all citizen users"""
        return self.filter(role='citizen')

    def fund_officers(self):
        """Get all fund officer users"""
        return self.filter(role='fund_officer')

    def fund_admins(self):
        """Get all fund admin users"""
        return self.filter(role='fund_admin')

    def admin_users(self):
        """Get all admin users (fund_admin and superadmin)"""
        return self.filter(role__in=['fund_admin', 'superadmin'])
