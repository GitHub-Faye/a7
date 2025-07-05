from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, 
    KnowledgePointViewSet, 
    CoursewareViewSet, 
    CourseContentGenerationViewSet,
    QuestionGenerationViewSet,
    ExerciseViewSet,
    StudentAnswerViewSet
)

# 创建路由并注册视图集
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'knowledge-points', KnowledgePointViewSet, basename='knowledge-point')
router.register(r'coursewares', CoursewareViewSet, basename='courseware')
router.register(r'course-content-generation', CourseContentGenerationViewSet, basename='course_content_generation')
router.register(r'question-generation', QuestionGenerationViewSet, basename='question-generation')
router.register(r'exercises', ExerciseViewSet)
router.register(r'student-answers', StudentAnswerViewSet)

# 生成URL配置
urlpatterns = [
    path('', include(router.urls)),
] 