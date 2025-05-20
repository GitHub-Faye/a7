from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Role
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, RoleSerializer
from .permissions import IsAdminOrReadOnly, IsUserOwnerOrStaff

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集，提供用户的增删改查功能
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsUserOwnerOrStaff]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsUserOwnerOrStaff]
        elif self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        获取当前登录用户的信息
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色视图集，提供角色的增删改查功能
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
