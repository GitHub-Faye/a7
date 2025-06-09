"""
AI服务应用URL路由配置
"""

from django.urls import path
from .views import N8nWebhookAPIView


app_name = 'ai_services'

urlpatterns = [
    path('webhook/', N8nWebhookAPIView.as_view(), name='webhook'),
] 