"""
课程应用的URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    KnowledgePointViewSet,
    CoursewareViewSet,
    ExerciseViewSet,
    StudentAnswerViewSet,
    QuestionGenerationViewSet,
    KnowledgePointToPPTViewSet,
    CourseContentGenerationViewSet
)

# 创建一个路由器并注册我们的视图集
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'knowledge-points', KnowledgePointViewSet)
router.register(r'courseware', CoursewareViewSet)
router.register(r'exercises', ExerciseViewSet)
router.register(r'student-answers', StudentAnswerViewSet)
router.register(r'knowledge-points-to-ppt', KnowledgePointToPPTViewSet, basename='knowledge-points-to-ppt')

# 注册AI服务相关视图集
router.register(r'generate-course', CourseContentGenerationViewSet, basename='generate-course')
router.register(r'generate-questions', QuestionGenerationViewSet, basename='generate-questions')

urlpatterns = [
    path('', include(router.urls)),
] 