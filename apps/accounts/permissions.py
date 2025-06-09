from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseRolePermission(permissions.BasePermission):
    """
    Base permission class for role-based access control
    """
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in self.allowed_roles


class IsCitizen(BaseRolePermission):
    """
    Permission for citizen users
    """
    allowed_roles = [User.UserRole.CITIZEN]


class IsFundOfficer(BaseRolePermission):
    """
    Permission for fund officer users
    """
    allowed_roles = [User.UserRole.FUND_OFFICER]


class IsFundAdmin(BaseRolePermission):
    """
    Permission for fund admin users
    """
    allowed_roles = [User.UserRole.FUND_ADMIN]


class IsSuperAdmin(BaseRolePermission):
    """
    Permission for super admin users
    """
    allowed_roles = [User.UserRole.SUPERADMIN]


class CanApplyForFunds(BaseRolePermission):
    """
    Permission for users who can apply for funds
    """
    allowed_roles = [User.UserRole.CITIZEN]


class CanReviewApplications(BaseRolePermission):
    """
    Permission for users who can review applications
    """
    allowed_roles = [
        User.UserRole.FUND_OFFICER,
        User.UserRole.FUND_ADMIN,
        User.UserRole.SUPERADMIN
    ]


class CanDeployContracts(BaseRolePermission):
    """
    Permission for users who can deploy smart contracts
    """
    allowed_roles = [
        User.UserRole.FUND_ADMIN,
        User.UserRole.SUPERADMIN
    ]


class IsAdminUser(BaseRolePermission):
    """
    Permission for admin users (fund_admin and superadmin)
    """
    allowed_roles = [
        User.UserRole.FUND_ADMIN,
        User.UserRole.SUPERADMIN
    ]


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows users to edit their own data or admins to edit any data
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_admin_user():
            return True

        # Users can only access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If the object is a User instance
        if isinstance(obj, User):
            return obj == request.user

        return False


class RoleBasedCRUDPermission(permissions.BasePermission):
    """
    Flexible permission class for CRUD operations based on user roles
    """

    def __init__(self, read_roles=None, write_roles=None, delete_roles=None):
        self.read_roles = read_roles or []
        self.write_roles = write_roles or []
        self.delete_roles = delete_roles or []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return request.user.role in self.read_roles
        elif request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.role in self.write_roles
        elif request.method == 'DELETE':
            return request.user.role in self.delete_roles

        return False
