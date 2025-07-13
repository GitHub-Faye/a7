"""
课程应用的URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'knowledge-points', views.KnowledgePointViewSet)
router.register(r'coursewares', views.CoursewareViewSet)
router.register(r'generate-content', views.CourseContentGenerationViewSet, basename='generate-content')
router.register(r'generate-questions', views.QuestionGenerationViewSet, basename='generate-questions')
router.register(r'exercises', views.ExerciseViewSet)
router.register(r'student-answers', views.StudentAnswerViewSet)
router.register(r'progress', views.ProgressTrackingViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
] 