"""
问题生成服务(generate_questions)与n8n集成测试

此测试文件验证问题生成服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
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
class GenerateQuestionsIntegrationTest(TestCase):
    """问题生成服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('generate-questions-list')  # 修正URL名称，不使用命名空间
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        self.course = Course.objects.create(
            title="物理力学", 
            description="经典力学基础知识",
            subject="物理",
            grade_level="高中",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="牛顿第二定律",
            content="力等于质量乘以加速度（F=ma），这个定律描述了物体加速度与施加力之间的关系。",
            importance=5
        )
    
    def test_generate_questions_api_structure(self):
        """测试问题生成API的请求和响应结构"""
        # 准备请求数据
        request_data = {
            'knowledge_point_ids': [self.knowledge_point.id],
            'question_types': ['single_choice', 'short_answer'],
            'quantity': 2,
            'difficulty': 3,
            'session_id': str(uuid.uuid4())
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
        self.assertIn('questions', response_data)
        self.assertIn('session_id', response_data)
        
        # 验证会话ID是否与请求中的相同
        self.assertEqual(response_data['session_id'], request_data['session_id'])
        
        # 验证问题列表
        questions = response_data['questions']
        self.assertIsInstance(questions, list)
        self.assertEqual(len(questions), request_data['quantity'])
        
        # 验证问题结构
        for question in questions:
            self.assertIn('title', question)
            self.assertIn('content', question)
            self.assertIn('type', question)
            self.assertIn('difficulty', question)
            self.assertIn('answer_template', question)
            
            # 验证问题类型是否符合请求中的类型
            self.assertIn(question['type'], request_data['question_types'])
            
            # 验证难度等级是否符合请求中的难度
            self.assertEqual(question['difficulty'], request_data['difficulty'])
    
    def test_generate_questions_error_handling(self):
        """测试问题生成API的错误处理"""
        # 准备无效的请求数据（缺少必需的knowledge_point_ids字段）
        request_data = {
            'question_types': ['single_choice'],
            'quantity': 2,
            'difficulty': 3
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
        
    def test_generate_questions_invalid_knowledge_point(self):
        """测试问题生成API使用不存在的知识点ID"""
        # 准备使用不存在的知识点ID的请求数据
        non_existent_id = 9999
        request_data = {
            'knowledge_point_ids': [non_existent_id],
            'question_types': ['single_choice'],
            'quantity': 2,
            'difficulty': 3
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