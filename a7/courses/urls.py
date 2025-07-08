from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由并注册视图集
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'knowledge-points', views.KnowledgePointViewSet)
router.register(r'courseware', views.CoursewareViewSet)
router.register(r'course-generate', views.CourseContentGenerationViewSet, basename='course-generate')
router.register(r'questions-generate', views.QuestionGenerationViewSet, basename='questions-generate')
router.register(r'exercises', views.ExerciseViewSet)
router.register(r'student-answers', views.StudentAnswerViewSet)
router.register(r'knowledge-points-to-ppt', views.KnowledgePointToPPTViewSet, basename='knowledge-points-to-ppt')

# 生成URL配置
urlpatterns = [
    path('', include(router.urls)),
] 