from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, KnowledgePointViewSet, CoursewareViewSet, CourseContentGenerationView

# 创建路由并注册视图集
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'knowledge-points', KnowledgePointViewSet, basename='knowledge-point')
router.register(r'coursewares', CoursewareViewSet, basename='courseware')

# 生成URL配置
urlpatterns = [
    path('', include(router.urls)),
    path('courses/generate-content/', CourseContentGenerationView.as_view(), name='course-generate-content'),
] 