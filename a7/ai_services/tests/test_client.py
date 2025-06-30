"""
n8n Webhook 客户端模块测试

此文件包含对 a7/ai_services/services/n8n_webhook/client.py 中
N8nWebhookClient 类的单元测试。
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ..models import WebhookConfig
from ..services.n8n_webhook.client import N8nWebhookClient
from ..services.n8n_webhook.exceptions import N8nResponseError

# 将测试标记为使用Django数据库和asyncio
pytestmark = [pytest.mark.django_db, pytest.mark.asyncio]

@pytest.fixture
def webhook_config():
    """提供一个测试用的 WebhookConfig 实例"""
    return WebhookConfig.objects.create(
        name="Test Webhook",
        url="http://fake-n8n-url.com/webhook",
        active=True
    )

@pytest.fixture
def valid_course_gen_request_data():
    """提供有效的课程生成请求数据"""
    return {
        "course_name": "量子物理",
        "chapter_count": 3,
        "course_description": "探索神奇的量子世界",
        "subject": "物理",
        "grade_level": "研究生"
    }

@pytest.fixture
def valid_course_gen_response_data():
    """提供有效的课程生成响应数据"""
    return {
        "course": {
            "title": "量子物理",
            "description": "探索神奇的量子世界",
            "subject": "物理",
            "grade_level": "研究生"
        },
        "knowledge_points": [
            {"title": "波粒二象性", "content": "...", "importance": 10, "children": []}
        ]
    }

class TestN8nWebhookClientCourseGeneration:
    """测试 N8nWebhookClient 中与课程生成相关的方法"""

    async def test_generate_course_content_success(
        self, webhook_config, valid_course_gen_request_data, valid_course_gen_response_data
    ):
        """测试 generate_course_content 方法在成功响应下的行为"""
        client = N8nWebhookClient(webhook_config=webhook_config)

        # 模拟 process_ai_task 方法返回成功结果
        with patch.object(client, 'process_ai_task', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = valid_course_gen_response_data
            
            result = await client.generate_course_content(valid_course_gen_request_data)
            
            # 验证 process_ai_task 是否以正确的参数被调用
            mock_process.assert_awaited_once_with("courseGeneration", valid_course_gen_request_data)
            
            # 验证返回结果是否符合预期
            assert result['course']['title'] == "量子物理"
            assert len(result['knowledge_points']) == 1

    async def test_generate_course_content_response_error(
        self, webhook_config, valid_course_gen_request_data
    ):
        """测试 generate_course_content 在响应错误时是否引发异常"""
        client = N8nWebhookClient(webhook_config=webhook_config)
        
        # 模拟 process_ai_task 方法引发 N8nResponseError
        with patch.object(client, 'process_ai_task', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = N8nResponseError("n8n返回了错误", status_code=500)
            
            with pytest.raises(N8nResponseError) as excinfo:
                await client.generate_course_content(valid_course_gen_request_data)
            
            assert excinfo.value.status_code == 500
            assert "n8n返回了错误" in str(excinfo.value)

    async def test_generate_course_content_invalid_response_data(
        self, webhook_config, valid_course_gen_request_data
    ):
        """测试 generate_course_content 在响应数据无效时是否引发异常"""
        client = N8nWebhookClient(webhook_config=webhook_config)
        
        # 模拟 process_ai_task 引发由 parse_response 导致的 N8nResponseError
        with patch.object(client, 'process_ai_task', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = N8nResponseError("响应数据格式无效", validation_errors=[])
            
            with pytest.raises(N8nResponseError) as excinfo:
                await client.generate_course_content(valid_course_gen_request_data)
            
            assert "响应数据格式无效" in str(excinfo.value)

    def test_generate_course_content_sync_success(
        webhook_config, valid_course_gen_request_data, valid_course_gen_response_data
    ):
        """测试 generate_course_content_sync 同步方法"""
        client = N8nWebhookClient(webhook_config=webhook_config)

        # 模拟异步方法以测试同步包装器
        with patch.object(client, 'generate_course_content', new_callable=AsyncMock) as mock_async_method:
            mock_async_method.return_value = valid_course_gen_response_data
            
            result = client.generate_course_content_sync(valid_course_gen_request_data)
            
            # 验证异步方法是否被调用
            mock_async_method.assert_awaited_once_with(valid_course_gen_request_data)
            
            # 验证返回结果
            assert result['course']['title'] == "量子物理" 