from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import UserProfile, LoginAttempt

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with role-based functionality
    """
    list_display = [
        'email', 'full_name', 'role', 'is_verified',
        'is_active', 'date_joined', 'last_login'
    ]
    list_filter = [
        'role', 'is_verified', 'is_active',
        'is_staff', 'date_joined'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Role & Access', {
            'fields': ('role', 'is_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Role & Access', {
            'fields': ('role', 'access_method')
        }),
    )

    readonly_fields = ['date_joined', 'last_login']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User profile admin
    """
    list_display = [
        'user', 'location', 'preferred_language', 'sms_notifications',
        'created_at'
    ]
    list_filter = ['preferred_language', 'sms_notifications', 'created_at']
    search_fields = ['user__email', 'user__first_name',
                     'user__last_name', 'location']

    fieldsets = (
        ('User Info', {'fields': ('user',)}),
        ('Profile Details', {
            'fields': ('avatar', 'bio', 'location', 'birth_date')
        }),
        ('Communication Settings', {
            'fields': ('preferred_language', 'sms_notifications', 'ussd_session_timeout')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Login attempt admin for security monitoring
    """
    list_display = [
        'email', 'user', 'method', 'successful_badge', 'ip_address',
        'timestamp'
    ]
    list_filter = ['method', 'successful', 'timestamp']
    search_fields = ['email', 'user__email', 'ip_address']
    ordering = ['-timestamp']

    readonly_fields = ['timestamp']

    def successful_badge(self, obj):
        if obj.successful:
            return format_html('<span style="color: green;">✓ Success</span>')
        else:
            return format_html('<span style="color: red;">✗ Failed</span>')
    successful_badge.short_description = 'Status'

    def has_add_permission(self, request):
        return False  # Prevent manual creation

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing
