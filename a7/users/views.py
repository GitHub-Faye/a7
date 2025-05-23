from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView
)

from .models import Role
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer, 
    RoleSerializer,
    PasswordChangeSerializer,
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    TokenVerifyResponseSerializer,
    TokenBlacklistResponseSerializer
)
from .permissions import (
    IsAdminOrReadOnly, 
    IsUserOwnerOrStaff,
    IsAdmin,
    IsTeacher,
    IsAdminOrTeacher,
    IsAdminOrTeacherReadOnly
)

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
            # 只有管理员可以创建用户
            self.permission_classes = [IsAdmin]
        elif self.action in ['update', 'partial_update']:
            # 管理员可以更新任何用户，普通用户只能更新自己
            self.permission_classes = [permissions.IsAuthenticated, IsUserOwnerOrStaff]
        elif self.action == 'destroy':
            # 只有管理员可以删除用户
            self.permission_classes = [IsAdmin]
        elif self.action == 'list':
            # 管理员和教师可以查看用户列表，但只有管理员可以修改
            self.permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacherReadOnly]
        elif self.action == 'me':
            # 任何已认证用户都可以查看自己的信息
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'change_password':
            # 任何已认证用户都可以修改自己的密码
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'my_permissions':
            # 任何已认证用户都可以查看自己的权限
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        获取当前登录用户的信息
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=PasswordChangeSerializer,
        responses={200: Response({"detail": "密码修改成功"})}
    )
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
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_permissions(self, request):
        """
        获取当前登录用户的所有权限
        """
        user = request.user
        # 获取用户的所有权限
        permissions = list(user.get_all_permissions())
        role_name = user.role
        
        return Response({
            'role': role_name,
            'permissions': permissions,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色视图集，提供角色的增删改查功能
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # 只有管理员可以管理角色，其他用户只能查看
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    # 添加查看角色权限的接口
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminOrReadOnly])
    def permissions(self, request, pk=None):
        """
        获取特定角色的所有权限
        """
        role = self.get_object()
        permissions = role.permissions.values_list('codename', flat=True)
        return Response({
            'role': role.name,
            'description': role.description,
            'permissions': list(permissions),
        })


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


class DecoratedTokenObtainPairView(CustomTokenObtainPairView):
    """
    自定义的令牌获取视图，同时为Swagger文档添加响应示例
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenRefreshView(TokenRefreshView):
    """
    装饰的令牌刷新视图，为Swagger文档添加响应示例
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenRefreshResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenVerifyView(TokenVerifyView):
    """
    装饰的令牌验证视图，为Swagger文档添加响应示例
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenVerifyResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenBlacklistView(TokenBlacklistView):
    """
    装饰的令牌黑名单视图，为Swagger文档添加响应示例
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenBlacklistResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    用户登出视图，将刷新令牌加入黑名单
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: Response({"detail": "登出成功，令牌已失效"}),
            status.HTTP_400_BAD_REQUEST: Response({"error": "需要提供refresh token"})
        }
    )
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
