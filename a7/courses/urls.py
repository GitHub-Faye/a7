from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

# 创建路由并注册视图集
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

# 生成URL配置
urlpatterns = [
    path('', include(router.urls)),
] 