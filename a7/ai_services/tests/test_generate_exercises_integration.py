"""
练习题生成服务(generate_exercises)与n8n集成测试

此测试文件验证练习题生成服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
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
class GenerateExercisesIntegrationTest(TestCase):
    """练习题生成服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('ai_services:generate-exercises-list')  # 基于视图集的URL名称
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        self.course = Course.objects.create(
            title="数学分析", 
            description="微积分与数学分析基础",
            subject="数学",
            grade_level="大学",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="导数概念",
            content="导数表示函数在某一点的瞬时变化率，是微积分的核心概念之一。",
            importance=5
        )
    
    def test_generate_exercises_api_structure(self):
        """测试练习题生成API的请求和响应结构"""
        # 准备请求数据
        request_data = {
            'query': '生成关于导数的练习题',
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
        self.assertIn('exercises', response_data)
        self.assertIn('session_id', response_data)
        
        # 验证会话ID是否与请求中的相同
        self.assertEqual(response_data['session_id'], request_data['session_id'])
        
        # 验证练习题列表
        exercises = response_data['exercises']
        self.assertIsInstance(exercises, list)
        
        # 验证练习题结构
        for exercise in exercises:
            self.assertIn('title', exercise)
            self.assertIn('content', exercise)
            self.assertIn('type', exercise)
            self.assertIn('difficulty', exercise)
            
            # 验证类型和难度级别
            self.assertIn(exercise['type'], ['single_choice', 'multiple_choice', 'short_answer', 'fill_in'])
            self.assertGreaterEqual(exercise['difficulty'], 1)
            self.assertLessEqual(exercise['difficulty'], 5)
    
    def test_generate_exercises_with_minimal_parameters(self):
        """测试使用最小参数集生成练习题"""
        # 只提供查询和会话ID
        request_data = {
            'query': '导数应用',
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
        
        # 验证响应数据结构
        self.assertIn('data', response.data)
        response_data = response.data['data']
        
        # 检查所需字段是否存在
        self.assertIn('exercises', response_data)
        self.assertIsInstance(response_data['exercises'], list)
        
        # 验证有练习题生成
        self.assertGreater(len(response_data['exercises']), 0)
    
    def test_generate_exercises_error_handling(self):
        """测试练习题生成API的错误处理"""
        # 准备无效的请求数据（缺少必需的query字段）
        request_data = {
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