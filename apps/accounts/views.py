from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile, LoginAttempt
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    AdminUserUpdateSerializer, PasswordChangeSerializer,
    UserProfileSerializer, LoginAttemptSerializer, UserStatsSerializer
)
from .permissions import (
    IsAdminUser, IsOwnerOrAdmin, CanAccessFrontend,
    IsSuperAdmin, CanReviewApplications
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view with login attempt tracking
    """

    def post(self, request, *args, **kwargs):
        ip_address = self.get_client_ip(request)
        email = request.data.get('email', '')

        response = super().post(request, *args, **kwargs)

        successful = response.status_code == 200
        user = None

        if successful and email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

        LoginAttempt.objects.create(
            user=user,
            email=email,
            ip_address=ip_address,
            method=LoginAttempt.LoginMethod.WEB,
            successful=successful,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user
    """
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()

        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone_number__icontains=search)
            )

        return queryset.order_by('-date_joined')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user instance
    """
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            if self.request.user.is_admin_user():
                return AdminUserUpdateSerializer
            return UserUpdateSerializer
        return UserSerializer


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update current user's information
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class PasswordChangeView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user)
        return profile


class UserStatsView(APIView):
    """
    Get user statistics (admin only)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'citizens': User.objects.filter(role=User.UserRole.CITIZEN).count(),
            'fund_officers': User.objects.filter(role=User.UserRole.FUND_OFFICER).count(),
            'fund_admins': User.objects.filter(role=User.UserRole.FUND_ADMIN).count(),
            'superadmins': User.objects.filter(role=User.UserRole.SUPERADMIN).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
        }

        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class LoginAttemptsView(generics.ListAPIView):
    """
    View login attempts (admin only)
    """
    serializer_class = LoginAttemptSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = LoginAttempt.objects.all()

        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by success status
        successful = self.request.query_params.get('successful')
        if successful is not None:
            queryset = queryset.filter(successful=successful.lower() == 'true')

        # Filter by time range
        hours = self.request.query_params.get('hours')
        if hours:
            try:
                hours_ago = timezone.now() - timedelta(hours=int(hours))
                queryset = queryset.filter(timestamp__gte=hours_ago)
            except ValueError:
                pass

        return queryset.order_by('-timestamp')


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def bulk_user_action(request):
    """
    Perform bulk actions on users (superadmin only)
    """
    action = request.data.get('action')
    user_ids = request.data.get('user_ids', [])

    if not action or not user_ids:
        return Response(
            {'error': 'Action and user_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    users = User.objects.filter(id__in=user_ids)

    if action == 'activate':
        users.update(is_active=True)
        message = f'{users.count()} users activated'
    elif action == 'deactivate':
        users.update(is_active=False)
        message = f'{users.count()} users deactivated'
    elif action == 'verify':
        users.update(is_verified=True)
        message = f'{users.count()} users verified'
    elif action == 'delete':
        count = users.count()
        users.delete()
        message = f'{count} users deleted'
    else:
        return Response(
            {'error': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({'message': message})


@api_view(['GET'])
@permission_classes([CanReviewApplications])
def users_by_role(request, role):
    """
    Get users filtered by role
    """
    if role not in [choice[0] for choice in User.UserRole.choices]:
        return Response(
            {'error': 'Invalid role'},
            status=status.HTTP_400_BAD_REQUEST
        )

    users = User.objects.filter(role=role, is_active=True)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
