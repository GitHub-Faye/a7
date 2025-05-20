from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .models import Role
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer, 
    RoleSerializer,
    PasswordChangeSerializer
)
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
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        修改用户密码
        """
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "密码修改成功"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色视图集，提供角色的增删改查功能
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义的令牌获取视图，返回用户信息和令牌
    """
    
    def post(self, request, *args, **kwargs):
        # 调用父类方法获取令牌
        response = super().post(request, *args, **kwargs)
        
        # 如果认证成功
        if response.status_code == 200:
            # 获取用户
            user = User.objects.get(username=request.data['username'])
            
            # 在响应中添加用户信息
            user_data = UserSerializer(user).data
            response.data.update({
                'user': user_data
            })
        
        return response


class LogoutView(APIView):
    """
    用户登出视图，将刷新令牌加入黑名单
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取请求中的refresh token
            refresh_token = request.data.get('refresh')
            
            if refresh_token:
                # 将refresh token加入黑名单
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                return Response(
                    {"detail": "登出成功，令牌已失效"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "需要提供refresh token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
