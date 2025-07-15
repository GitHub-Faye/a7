"""
课程内容生成服务(generate_course_content)与n8n集成测试

此测试文件验证课程内容生成服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
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
class GenerateCourseContentIntegrationTest(TestCase):
    """课程内容生成服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('generate-content-list')  # 修正URL名称，不使用命名空间
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        
        # 登录用户
        self.client.force_authenticate(user=self.teacher)
    
    def test_generate_course_content_api_structure(self):
        """测试课程内容生成API的请求和响应结构"""
        # 准备请求数据
        request_data = {
            'course_name': 'TensorFlow.js应用开发',
            'chapter_count': 10,
            'course_description': 'TensorFlow.js应用开发',
            'subject': '计算机科学',
            'grade_level': '大学一年级',
            'additional_requirements': '包含实践练习',
            'session_id': str(uuid.uuid4())
        }
        
        # 发送请求
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证响应状态码和结构
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # 验证响应数据结构是否符合统一标准
        self.assertIn('data', response.data)
        response_data = response.data['data']
        
        # 检查所需字段是否存在
        self.assertIn('id', response_data)
        self.assertIn('title', response_data)
        self.assertIn('description', response_data)
        self.assertIn('subject', response_data)
        self.assertIn('grade_level', response_data)
        
        # 验证课程信息是否与请求匹配
        self.assertEqual(response_data['title'], request_data['course_name'])
        self.assertEqual(response_data['description'], request_data['course_description'])
        self.assertEqual(response_data['subject'], request_data['subject'])
        self.assertEqual(response_data['grade_level'], request_data['grade_level'])
    
    def test_generate_course_content_error_handling(self):
        """测试课程内容生成API的错误处理"""
        # 准备无效的请求数据（缺少必需的course_name字段）
        request_data = {
            'chapter_count': 5,
            'course_description': '入门级Python编程课程',
            'subject': '计算机科学',
            'grade_level': '大学一年级'
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
    
    def test_generate_course_content_unauthorized(self):
        """测试未认证用户无法生成课程内容"""
        # 创建新客户端，不进行认证
        client = APIClient()
        
        # 准备请求数据
        request_data = {
            'course_name': 'Python编程基础',
            'chapter_count': 5,
            'course_description': '入门级Python编程课程',
            'subject': '计算机科学',
            'grade_level': '大学一年级'
        }
        
        # 发送请求
        response = client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证未认证用户被拒绝
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

