from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # 示例路由，实际开发时可以替换
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
] 