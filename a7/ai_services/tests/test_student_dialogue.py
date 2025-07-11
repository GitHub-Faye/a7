"""
学生对话API测试模块
"""
import uuid
import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.serializers import StudentDialogueSerializer
from ai_services.services.n8n_webhook.formats import (
    DialogueRequestData, 
    DialogueResponseData,
    format_student_dialogue_response
)
from ai_services.services.n8n_webhook.client import N8nWebhookClient


class StudentDialogueSerializerTest(TestCase):
    """学生对话序列化器测试类"""
    
    def test_serializer_valid_data(self):
        """测试序列化器接受有效数据"""
        data = {
            'query': '什么是机器学习？',
            'session_id': str(uuid.uuid4()),
            'context': {'course_id': 1}
        }
        serializer = StudentDialogueSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_missing_query(self):
        """测试序列化器拒绝缺少查询文本的数据"""
        data = {
            'query': '',
            'session_id': str(uuid.uuid4())
        }
        serializer = StudentDialogueSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('query', serializer.errors)
    
    def test_serializer_invalid_context(self):
        """测试序列化器拒绝无效上下文格式的数据"""
        data = {
            'query': '什么是机器学习？',
            'session_id': str(uuid.uuid4()),
            'context': 'invalid_context'  # 应该是字典而不是字符串
        }
        serializer = StudentDialogueSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('context', serializer.errors)
    
    def test_serializer_auto_session_id(self):
        """测试缺少会话ID时序列化器不会报错"""
        data = {
            'query': '什么是机器学习？',
        }
        serializer = StudentDialogueSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        

class DialogueFormatsTest(TestCase):
    """学生对话数据模型和格式化函数测试类"""
    
    def test_request_data_model(self):
        """测试DialogueRequestData模型"""
        data = {
            'query': '什么是机器学习？',
            'sessionId': str(uuid.uuid4()),
            'context': {'course_id': 1}
        }
        request_model = DialogueRequestData(**data)
        self.assertEqual(request_model.query, data['query'])
        self.assertEqual(request_model.sessionId, data['sessionId'])
        self.assertEqual(request_model.context, data['context'])
    
    def test_response_data_model(self):
        """测试DialogueResponseData模型"""
        data = {
            'answer': '机器学习是人工智能的一个子领域...',
            'resources': [
                {
                    'title': '机器学习基础',
                    'content': '机器学习介绍',
                    'type': '知识点',
                    'id': 1
                }
            ],
            'follow_up_questions': ['什么是深度学习？', '机器学习有哪些应用？']
        }
        response_model = DialogueResponseData(**data)
        self.assertEqual(response_model.answer, data['answer'])
        self.assertEqual(len(response_model.resources), 1)
        self.assertEqual(response_model.resources[0].title, data['resources'][0]['title'])
        self.assertEqual(len(response_model.follow_up_questions), 2)
    
    def test_format_student_dialogue_response_with_answer_field(self):
        """测试格式化带有answer字段的原始响应"""
        raw_data = {
            'answer': '机器学习是人工智能的一个子领域...'
        }
        formatted = format_student_dialogue_response(raw_data)
        self.assertEqual(formatted['answer'], raw_data['answer'])
        self.assertIn('resources', formatted)
        self.assertIn('follow_up_questions', formatted)
    
    def test_format_student_dialogue_response_with_string_input(self):
        """测试格式化字符串响应"""
        raw_data = '机器学习是人工智能的一个子领域...'
        formatted = format_student_dialogue_response(raw_data)
        self.assertEqual(formatted['answer'], raw_data)
        self.assertIn('resources', formatted)
        self.assertIn('follow_up_questions', formatted)


class StudentDialogueApiTest(TestCase):
    """学生对话API端点测试类"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('student-dialogue-list')  # 基于viewset名称
        
        # 模拟的AI响应数据
        self.mock_response = {
            'answer': '机器学习是人工智能的一个子领域，它使用统计技术让计算机能够从数据中"学习"（即逐步提高性能）而无需明确编程。',
            'resources': [
                {
                    'title': '机器学习基础',
                    'content': '机器学习介绍与基本概念',
                    'type': '知识点',
                    'id': 1
                }
            ],
            'follow_up_questions': ['什么是深度学习？', '机器学习有哪些应用？']
        }
    
    @patch('ai_services.views.N8nWebhookClient')
    def test_create_dialogue(self, mock_client_class):
        """测试创建对话请求"""
        # 设置模拟客户端的返回值
        mock_client_instance = MagicMock()
        mock_client_instance.dialogue_with_student_sync.return_value = self.mock_response
        mock_client_class.return_value = mock_client_instance
        
        # 创建请求数据
        request_data = {
            'query': '什么是机器学习？',
            'session_id': str(uuid.uuid4()),
            'context': {'course_id': 1}
        }
        
        # 发送请求并检查响应
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['answer'], self.mock_response['answer'])
        self.assertEqual(len(response.data['data']['resources']), 1)
        self.assertEqual(len(response.data['data']['follow_up_questions']), 2)
        self.assertIn('session_id', response.data['data'])
        
        # 验证客户端调用
        mock_client_instance.dialogue_with_student_sync.assert_called_once()
        call_args = mock_client_instance.dialogue_with_student_sync.call_args[0][0]
        self.assertEqual(call_args['query'], request_data['query'])
        self.assertEqual(call_args['sessionId'], request_data['session_id'])
        self.assertEqual(call_args['context'], request_data['context'])
    
    @patch('ai_services.views.N8nWebhookClient')
    def test_create_dialogue_without_session_id(self, mock_client_class):
        """测试创建对话请求时自动生成会话ID"""
        # 设置模拟客户端的返回值
        mock_client_instance = MagicMock()
        mock_client_instance.dialogue_with_student_sync.return_value = self.mock_response
        mock_client_class.return_value = mock_client_instance
        
        # 创建请求数据 (无会话ID)
        request_data = {
            'query': '什么是机器学习？'
        }
        
        # 发送请求并检查响应
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('session_id', response.data['data'])
        
        # 验证客户端调用
        mock_client_instance.dialogue_with_student_sync.assert_called_once()
        call_args = mock_client_instance.dialogue_with_student_sync.call_args[0][0]
        self.assertEqual(call_args['query'], request_data['query'])
        self.assertIn('sessionId', call_args)
    
    @patch('ai_services.views.N8nWebhookClient')
    def test_create_dialogue_with_error(self, mock_client_class):
        """测试处理对话请求中的错误"""
        # 设置模拟客户端抛出异常
        mock_client_instance = MagicMock()
        mock_client_instance.dialogue_with_student_sync.side_effect = Exception("AI服务暂时不可用")
        mock_client_class.return_value = mock_client_instance
        
        # 创建请求数据
        request_data = {
            'query': '什么是机器学习？'
        }
        
        # 发送请求并检查响应
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应是否包含错误信息
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
    
    def test_empty_query(self):
        """测试空查询的验证"""
        request_data = {
            'query': ''  # 空查询
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应是否包含错误信息
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR') 