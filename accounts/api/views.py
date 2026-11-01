"""
Accounts API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth import login, logout
from django.utils.translation import gettext_lazy as _
from .serializers import (
    UserSerializer, UserListSerializer, LoginSerializer, 
    PasswordChangeSerializer, CheckUsernameSerializer
)
from accounts.models import User


class UserViewSet(viewsets.ModelViewSet):
    """User CRUD operations"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [permissions.IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def perform_create(self, serializer):
        user = serializer.save()
        if not user.pk:
            user.save()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class LoginView(APIView):
    """User login"""
    
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        login(request, user)
        
        # Set session expiry based on remember_me
        if not serializer.validated_data.get('remember_me', False):
            request.session.set_expiry(0)
        
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'message': _('Login successful')
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """User logout"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': _('Logout successful')}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """User profile management"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordChangeView(APIView):
    """Password change"""
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password1'])
        user.save()
        
        # Update session auth hash
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return Response({'message': _('Password changed successfully')}, status=status.HTTP_200_OK)


class CheckUsernameView(APIView):
    """Check username availability"""
    
    serializer_class = CheckUsernameSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        username = request.query_params.get('username', '')
        serializer = self.serializer_class(data={'username': username})
        serializer.is_valid(raise_exception=True)
        return Response({'available': True})
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({'available': True})
        return Response({'available': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
