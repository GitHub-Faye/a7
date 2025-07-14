"""
学生对话服务(dialogue_with_student)与n8n集成测试

此测试文件验证学生对话服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
"""

import json
import uuid
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Course, KnowledgePoint
from users.models import User
from ai_services.services.n8n_webhook.client import N8nWebhookClient


@pytest.mark.integration  # 标记为集成测试
class DialogueWithStudentIntegrationTest(TestCase):
    """学生对话服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('ai_services:student-dialogue-list')  # 基于视图集的URL名称
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        self.course = Course.objects.create(
            title="人工智能导论", 
            description="人工智能基础知识介绍",
            subject="计算机科学",
            grade_level="大学",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="机器学习基础",
            content="机器学习是人工智能的一个子领域，专注于开发能够从数据中学习的算法和模型。",
            importance=5
        )
    
    def test_dialogue_with_student_api_structure(self):
        """测试学生对话API的请求和响应结构"""
        # 准备请求数据
        session_id = str(uuid.uuid4())
        request_data = {
            'query': '什么是机器学习？',
            'session_id': session_id,
            'context': {
                'previous_messages': [
                    {'role': 'user', 'content': '人工智能是什么？'},
                    {'role': 'assistant', 'content': '人工智能是计算机科学的一个分支，致力于开发能够模拟人类智能行为的系统。'}
                ]
            }
        }
        
        # 发送请求
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应状态码和结构
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证响应数据结构是否符合统一标准
        self.assertIn('data', response.data)
        response_data = response.data['data']
        
        # 检查所需字段是否存在
        self.assertIn('answer', response_data)
        self.assertIn('session_id', response_data)
        self.assertIn('sources', response_data)
        # 不再检查resources字段，因为它已被sources字段替代
        self.assertIn('follow_up_questions', response_data)
        
        # 验证会话ID是否与请求中的相同
        self.assertEqual(response_data['session_id'], session_id)
        
        # 验证答案不为空
        self.assertTrue(len(response_data['answer']) > 0)
    
    def test_dialogue_with_student_error_handling(self):
        """测试学生对话API的错误处理"""
        # 准备无效的请求数据（缺少必需的query字段）
        request_data = {
            'session_id': str(uuid.uuid4()),
            'context': {}
        }
        
        # 发送请求
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error_code', response.data)
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR') 