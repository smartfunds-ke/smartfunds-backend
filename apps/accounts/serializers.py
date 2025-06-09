from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile, LoginAttempt

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'location', 'birth_date',
            'preferred_language', 'sms_notifications', 'ussd_session_timeout'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for general use
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'access_method', 'is_verified',
            'is_active', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_verified']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    """
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'phone_number', 'role', 'access_method'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def validate_role(self, value):
        """
        Validate role assignment based on current user's permissions
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user

            # Only superadmin can create other superadmins
            if value == User.UserRole.SUPERADMIN and current_user.role != User.UserRole.SUPERADMIN:
                raise serializers.ValidationError(
                    "Only superadmin can create superadmin users."
                )

            # Only admins can create fund_admin and fund_officer users
            admin_roles = [User.UserRole.FUND_ADMIN,
                           User.UserRole.FUND_OFFICER]
            if value in admin_roles and not current_user.is_admin_user():
                raise serializers.ValidationError(
                    "Only admin users can create admin or officer roles."
                )

        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'access_method'
        ]

    def validate_phone_number(self, value):
        """
        Ensure phone number is unique (excluding current user)
        """
        if User.objects.exclude(pk=self.instance.pk).filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "This phone number is already in use.")
        return value


class AdminUserUpdateSerializer(UserUpdateSerializer):
    """
    Serializer for admin users to update user information
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'role',
            'access_method', 'is_active', 'is_verified'
        ]

    def validate_role(self, value):
        """
        Validate role changes based on current user's permissions
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user

            # Only superadmin can modify superadmin role
            if (value == User.UserRole.SUPERADMIN or
                self.instance.role == User.UserRole.SUPERADMIN) and \
               current_user.role != User.UserRole.SUPERADMIN:
                raise serializers.ValidationError(
                    "Only superadmin can modify superadmin roles."
                )

        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for login attempts
    """
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email', 'ip_address', 'method', 'successful',
            'timestamp', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user statistics
    """
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    citizens = serializers.IntegerField()
    fund_officers = serializers.IntegerField()
    fund_admins = serializers.IntegerField()
    superadmins = serializers.IntegerField()
    verified_users = serializers.IntegerField()
