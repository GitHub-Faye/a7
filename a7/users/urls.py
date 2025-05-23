from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, RoleViewSet, DecoratedTokenObtainPairView, LogoutView

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 登录和登出路径
    path('login/', DecoratedTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
] 