"""
AI服务应用URL路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseContentGenerationViewSet,
    QuestionGenerationViewSet,
    StudentDialogueViewSet
)

app_name = 'ai_services'

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'generate-course', CourseContentGenerationViewSet, basename='generate-course')
router.register(r'generate-questions', QuestionGenerationViewSet, basename='generate-questions')
router.register(r'student-dialogue', StudentDialogueViewSet, basename='student-dialogue')

urlpatterns = [
    path('', include(router.urls)),
] 