"""
AI服务应用URL路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StudentDialogueViewSet,
    ExerciseGenerationViewSet,
    StudentAnswerCorrectionViewSet,
    TeachingOutlineViewSet,
    ExamOutlineViewSet,
    LessonPlanViewSet
)

app_name = 'ai_services'

# 创建路由器并注册视图集
router = DefaultRouter()
# 移除已删除的QuestionGenerationViewSet
router.register(r'student-dialogue', StudentDialogueViewSet, basename='student-dialogue')
router.register(r'generate-exercises', ExerciseGenerationViewSet, basename='generate-exercises')
router.register(r'correct-answer', StudentAnswerCorrectionViewSet, basename='correct-answer')
router.register(r'generate/teaching-outline', TeachingOutlineViewSet, basename='teaching-outline')
router.register(r'generate/exam-outline', ExamOutlineViewSet, basename='exam-outline')
router.register(r'generate/lesson-plan', LessonPlanViewSet, basename='lesson-plan')

urlpatterns = [
    path('', include(router.urls)),
] 