from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    CustomTokenObtainPairView, UserListCreateView, UserDetailView,
    CurrentUserView, PasswordChangeView, UserProfileView,
    UserStatsView, LoginAttemptsView, bulk_user_action,
    users_by_role,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User management endpoints
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/stats/', UserStatsView.as_view(), name='user-stats'),
    path('users/bulk-action/', bulk_user_action, name='bulk-user-action'),
    path('users/role/<str:role>/', users_by_role, name='users-by-role'),

    # Profile and settings
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),

    # Security and monitoring
    path('login-attempts/', LoginAttemptsView.as_view(), name='login-attempts'),
]
