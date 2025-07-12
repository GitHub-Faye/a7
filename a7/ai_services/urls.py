"""
AI服务应用URL路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StudentDialogueViewSet,
    ExerciseGenerationViewSet,
    StudentAnswerCorrectionViewSet
)

app_name = 'ai_services'

# 创建路由器并注册视图集
router = DefaultRouter()
# 移除已删除的QuestionGenerationViewSet
router.register(r'student-dialogue', StudentDialogueViewSet, basename='student-dialogue')
router.register(r'generate-exercises', ExerciseGenerationViewSet, basename='generate-exercises')
router.register(r'correct-answer', StudentAnswerCorrectionViewSet, basename='correct-answer')

urlpatterns = [
    path('', include(router.urls)),
] 