"""
学生对话API与真实n8n AI服务的集成测试
"""
import json
import uuid
import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from courses.serializers import StudentDialogueSerializer
from ai_services.services.n8n_webhook.client import N8nWebhookClient
from ai_services.services.n8n_webhook.exceptions import N8nWebhookError


@pytest.mark.integration  # 标记为集成测试，可以选择性跳过
class StudentDialogueIntegrationTest(TestCase):
    """学生对话API与真实n8n AI服务的集成测试类"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('student-dialogue-list')  # 基于viewset名称
        
    def test_real_n8n_dialogue(self):
        """测试与真实n8n AI服务的对话集成
        
        注意：此测试需要n8n服务可用，并且配置了正确的webhook URL。
        如果n8n服务不可用，此测试将失败。
        """
        # 创建请求数据
        request_data = {
            'query': '什么是人工智能？',
            'session_id': str(uuid.uuid4()),
            'context': {'test_mode': True}
        }
        
        # 发送请求
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证响应数据结构
        self.assertIn('data', response.data)
        self.assertIn('answer', response.data['data'])
        self.assertIn('session_id', response.data['data'])
        
        # 验证答案不为空
        self.assertTrue(len(response.data['data']['answer']) > 0)
        
        # 打印实际响应以便手动检查
        print(f"\n实际AI回答: {response.data['data']['answer'][:100]}...")
    
    def test_multi_turn_dialogue(self):
        """测试多轮对话
        
        注意：此测试需要n8n服务可用，并且配置了正确的webhook URL。
        如果n8n服务不可用，此测试将失败。
        """
        # 第一轮对话
        session_id = str(uuid.uuid4())
        first_request = {
            'query': '什么是机器学习？',
            'session_id': session_id
        }
        
        first_response = self.client.post(
            self.url,
            data=json.dumps(first_request),
            content_type='application/json'
        )
        
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', first_response.data['data'])
        
        # 第二轮对话，引用第一轮
        second_request = {
            'query': '它与深度学习有什么区别？',
            'session_id': session_id  # 使用相同的会话ID
        }
        
        second_response = self.client.post(
            self.url,
            data=json.dumps(second_request),
            content_type='application/json'
        )
        
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', second_response.data['data'])
        
        # 打印实际响应以便手动检查
        print(f"\n第二轮对话回答: {second_response.data['data']['answer'][:100]}...")
        
        # 验证第二轮回答中包含相关术语（这是一个简单的相关性检查）
        answer_lower = second_response.data['data']['answer'].lower()
        self.assertTrue(
            '深度学习' in answer_lower or 
            '机器学习' in answer_lower or
            'deep learning' in answer_lower or
            'machine learning' in answer_lower
        )


class StudentDialogueErrorHandlingTest(TestCase):
    """学生对话API错误处理和边界情况测试类"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('student-dialogue-list')
    
    def test_empty_query(self):
        """测试空查询"""
        request_data = {
            'query': '',
            'session_id': str(uuid.uuid4())
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
    
    def test_long_query(self):
        """测试超长查询"""
        # 创建一个10000字符的查询
        long_query = 'a' * 10000
        
        request_data = {
            'query': long_query,
            'session_id': str(uuid.uuid4())
        }
        
        # 实际调用API
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 即使查询很长，API也应该能够处理
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_invalid_json(self):
        """测试无效的JSON请求体"""
        # 发送无效的JSON
        response = self.client.post(
            self.url,
            data="这不是有效的JSON",
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.dialogue_with_student_sync')
    def test_n8n_webhook_error(self, mock_dialogue):
        """测试n8n webhook错误处理"""
        # 模拟N8nWebhookError异常
        mock_dialogue.side_effect = N8nWebhookError("n8n服务暂时不可用")
        
        request_data = {
            'query': '什么是人工智能？',
            'session_id': str(uuid.uuid4())
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "n8n服务暂时不可用")
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.dialogue_with_student_sync')
    def test_general_exception(self, mock_dialogue):
        """测试一般异常处理"""
        # 模拟一般异常
        mock_dialogue.side_effect = Exception("未知错误")
        
        request_data = {
            'query': '什么是人工智能？',
            'session_id': str(uuid.uuid4())
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertIn("未知错误", response.data['message']) 