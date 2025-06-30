"""
AI服务视图集成测试

此文件包含对 a7/ai_services/views.py 中 API 视图的端到端集成测试。
"""
import pytest
from unittest.mock import patch

from rest_framework.test import APIClient
from courses.models import Course, KnowledgePoint
from users.models import User
from ..models import WebhookConfig

# 标记所有测试都使用Django数据库
pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    """提供一个API客户端实例"""
    return APIClient()

@pytest.fixture
def authenticated_user(api_client):
    """创建一个已认证的用户并将其附加到API客户端"""
    user = User.objects.create_user(username='testuser', password='password123', role='teacher')
    api_client.force_authenticate(user=user)
    return user

@pytest.fixture
def webhook_config():
    """提供一个测试用的 WebhookConfig 实例"""
    return WebhookConfig.objects.create(
        name="Default Webhook",
        url="http://fake-n8n-url.com/webhook",
        active=True
    )

@pytest.fixture
def valid_ai_response_data():
    """提供一个从n8n返回的有效的、包含层级结构的AI响应数据"""
    return {
        "course": {
            "title": "量子物理入门",
            "description": "从零开始探索神奇的量子世界",
            "subject": "物理",
            "grade_level": "大学"
        },
        "knowledge_points": [
            {
                "title": "波粒二象性", "content": "...", "importance": 10,
                "children": [
                    {"title": "光电效应", "content": "...", "importance": 9, "children": []}
                ]
            }
        ]
    }

class TestN8nWebhookAPIViewIntegration:
    """测试 N8nWebhookAPIView 的集成流程"""

    def test_course_generation_e2e_success(
        self, api_client, authenticated_user, webhook_config, valid_ai_response_data
    ):
        """测试课程生成的端到端成功流程"""
        
        request_data = {
            "task_type": "courseGeneration",
            "data": {
                "course_name": "量子物理入门",
                "chapter_count": 1
            }
        }
        
        # 修正: 模拟整个N8nWebhookClient类，以绕过其__init__方法中的URL检查
        with patch('ai_services.views.N8nWebhookClient') as MockN8nClient:
            # 配置模拟实例及其方法的返回值
            mock_instance = MockN8nClient.return_value
            mock_instance.process_ai_task_sync.return_value = valid_ai_response_data
            
            # 发送POST请求到API端点
            response = api_client.post('/api/ai/webhook/', request_data, format='json')
            
            # 1. 验证API响应
            assert response.status_code == 201
            response_json = response.json()
            assert response_json['success'] is True
            assert 'course_id' in response_json['data']
            
            # 2. 验证数据库状态
            course_id = response_json['data']['course_id']
            assert Course.objects.filter(id=course_id).exists()
            
            # 确认创建了一个课程和两个知识点（一个顶级，一个子级）
            assert Course.objects.count() == 1
            assert KnowledgePoint.objects.count() == 2
            
            # 验证知识点的层级关系
            course = Course.objects.get(id=course_id)
            assert course.knowledge_points.count() == 2 # 检查所有关联的知识点
            assert course.knowledge_points.filter(parent=None).count() == 1 # 检查顶层知识点
            
            # 3. 验证模拟方法是否被正确调用
            mock_instance.process_ai_task_sync.assert_called_once_with("courseGeneration", request_data['data']) 