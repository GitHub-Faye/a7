"""
知识点处理API端点测试模块
"""

import json
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User, Role
from courses.models import Course, KnowledgePoint
from ai_services.services.n8n_webhook.client import N8nWebhookClient


class KnowledgePointProcessingAPITestCase(TestCase):
    """知识点处理API测试用例"""
    
    def setUp(self):
        """测试准备"""
        # 创建测试用户
        self.admin_role = Role.objects.create(name="admin")
        self.teacher_role = Role.objects.create(name="teacher")
        self.student_role = Role.objects.create(name="student")
        
        self.admin_user = User.objects.create_user(
            username="admin", 
            email="admin@example.com", 
            password="password123"
        )
        self.admin_user.role_obj = self.admin_role
        self.admin_user.save()
        
        self.teacher_user = User.objects.create_user(
            username="teacher", 
            email="teacher@example.com", 
            password="password123"
        )
        self.teacher_user.role_obj = self.teacher_role
        self.teacher_user.save()
        
        self.student_user = User.objects.create_user(
            username="student", 
            email="student@example.com", 
            password="password123"
        )
        self.student_user.role_obj = self.student_role
        self.student_user.save()
        
        # 创建测试课程和知识点
        self.course = Course.objects.create(
            title="测试课程",
            description="这是一个测试课程",
            subject="计算机科学",
            grade_level="大学",
            teacher=self.teacher_user
        )
        
        self.knowledge_point1 = KnowledgePoint.objects.create(
            title="Python基础",
            content="Python是一种解释型、高级、通用型编程语言。",
            importance=8,
            course=self.course
        )
        
        self.knowledge_point2 = KnowledgePoint.objects.create(
            title="数据结构",
            content="数据结构是计算机存储、组织数据的方式。",
            importance=9,
            course=self.course,
            parent=self.knowledge_point1
        )
        
        # 准备测试客户端
        self.client = APIClient()
        
        # 准备请求数据
        self.valid_data = {
            "knowledge_points": [
                {
                    "id": self.knowledge_point1.id,
                    "title": self.knowledge_point1.title,
                    "content": self.knowledge_point1.content
                },
                {
                    "id": self.knowledge_point2.id,
                    "title": self.knowledge_point2.title,
                    "content": self.knowledge_point2.content
                }
            ],
            "title": "Python编程课程",
            "subject": "计算机科学",
            "grade_level": "大学",
            "additional_requirements": "注重实践案例"
        }
        
        self.invalid_data = {
            "knowledge_points": [],  # 空列表，应该验证失败
            "title": "Python编程课程",
            "subject": "计算机科学",
            "grade_level": "大学"
        }
        
        # 模拟响应数据
        self.mock_response = {
            "content": "这是一个生成的教学大纲内容...",
            "structure": {
                "第一章": "Python基础语法",
                "第二章": "数据结构与算法"
            },
            "sources": [
                {
                    "title": "Python官方文档",
                    "url": "https://docs.python.org/"
                }
            ],
            "session_id": "test-session-id"  # 修改：将sessionId改为session_id以匹配API响应格式
        }
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_teaching_outline_sync')
    def test_teaching_outline_api_success(self, mock_generate):
        """测试教学大纲API成功情况"""
        # 设置模拟返回值
        mock_generate.return_value = self.mock_response
        
        # 登录教师用户
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        url = reverse('ai_services:teaching-outline-list')
        response = self.client.post(url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "教学大纲生成成功")
        self.assertEqual(response.data['data']['content'], self.mock_response['content'])
        self.assertEqual(response.data['data']['structure'], self.mock_response['structure'])
        self.assertEqual(response.data['data']['session_id'], self.mock_response['session_id'])  # 修改：使用session_id而不是sessionId
        
        # 验证模拟函数被调用
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        self.assertEqual(args[0]['knowledge_points'], self.valid_data['knowledge_points'])
        self.assertEqual(args[0]['title'], self.valid_data['title'])
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_exam_outline_sync')
    def test_exam_outline_api_success(self, mock_generate):
        """测试考试大纲API成功情况"""
        # 设置模拟返回值
        mock_generate.return_value = self.mock_response
        
        # 登录教师用户
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        url = reverse('ai_services:exam-outline-list')
        response = self.client.post(url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "考试大纲生成成功")
        self.assertEqual(response.data['data']['content'], self.mock_response['content'])
        
        # 验证模拟函数被调用
        mock_generate.assert_called_once()
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_lesson_plan_sync')
    def test_lesson_plan_api_success(self, mock_generate):
        """测试教案API成功情况"""
        # 设置模拟返回值
        mock_generate.return_value = self.mock_response
        
        # 登录教师用户
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        url = reverse('ai_services:lesson-plan-list')
        response = self.client.post(url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "教案生成成功")
        self.assertEqual(response.data['data']['content'], self.mock_response['content'])
        
        # 验证模拟函数被调用
        mock_generate.assert_called_once()
    
    def test_teaching_outline_api_validation_error(self):
        """测试教学大纲API验证错误情况"""
        # 登录教师用户
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        url = reverse('ai_services:teaching-outline-list')
        response = self.client.post(url, self.invalid_data, format='json')
        
        # 验证响应状态码和success标志
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # 由于中间件修改了响应格式，我们只检查错误码
        self.assertEqual(response.data['error_code'], "VALIDATION_ERROR")
        
        # 检查message字段是否存在，但不检查具体内容
        self.assertIn('message', response.data)
    
    def test_authentication_required(self):
        """测试需要认证"""
        # 不登录
        self.client.force_authenticate(user=None)
        
        # 发送请求
        url = reverse('ai_services:teaching-outline-list')
        response = self.client.post(url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 