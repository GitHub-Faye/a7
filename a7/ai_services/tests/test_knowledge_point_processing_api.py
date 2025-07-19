"""
知识点处理API测试模块

测试教学大纲、考试大纲和教案生成API端点
"""

import json
import uuid
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User, Role
from ai_services.services.n8n_webhook.exceptions import N8nWebhookError


class KnowledgePointProcessingAPITestCase(APITestCase):
    """知识点处理API测试用例"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建测试用户和角色
        self.admin_role = Role.objects.create(name="admin")
        self.teacher_role = Role.objects.create(name="teacher")
        self.student_role = Role.objects.create(name="student")
        
        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123"
        )
        self.admin_user.role = "admin"  # 设置角色字符串
        self.admin_user.role_obj = self.admin_role  # 设置角色对象
        self.admin_user.save()
        
        # 创建教师用户
        self.teacher_user = User.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="password123"
        )
        self.teacher_user.role = "teacher"  # 设置角色字符串
        self.teacher_user.role_obj = self.teacher_role  # 设置角色对象
        self.teacher_user.save()
        
        # 创建学生用户
        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="password123"
        )
        self.student_user.role = "student"  # 设置角色字符串
        self.student_user.role_obj = self.student_role  # 设置角色对象
        self.student_user.save()
        
        # 测试数据
        self.valid_knowledge_points = [
            {
                "title": "函数的概念",
                "content": "函数是描述两个变量之间对应关系的数学概念",
                "importance": 8
            },
            {
                "title": "函数的表示方法",
                "content": "函数可以用解析式、表格、图像等方式表示",
                "importance": 7
            }
        ]
        
        self.valid_payload = {
            "knowledge_points": self.valid_knowledge_points,
            "title": "高中数学函数教学大纲",
            "subject": "数学",
            "grade_level": "高中",
            "additional_requirements": "侧重函数应用",
            "session_id": str(uuid.uuid4())
        }
        
        # API端点
        self.teaching_outline_url = reverse('ai_services:teaching-outline-list')
        self.exam_outline_url = reverse('ai_services:exam-outline-list')
        self.lesson_plan_url = reverse('ai_services:lesson-plan-list')
        
        # 模拟响应数据
        self.mock_response = {
            "content": "这是生成的内容",
            "structure": {"第一章": "函数概念", "第二章": "函数应用"},
            "sources": [{"title": "高中数学教材", "url": "http://example.com"}],
            "session_id": str(uuid.uuid4())
        }
    
    def test_teaching_outline_unauthorized(self):
        """测试未认证用户无法访问教学大纲生成API"""
        response = self.client.post(self.teaching_outline_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_teaching_outline_student_forbidden(self):
        """测试学生用户无法访问教学大纲生成API"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.teaching_outline_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_teaching_outline_sync')
    def test_teaching_outline_success(self, mock_generate):
        """测试教学大纲生成API成功情况"""
        # 设置模拟返回值
        mock_generate.return_value = self.mock_response
        
        # 使用教师用户认证
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        response = self.client.post(self.teaching_outline_url, self.valid_payload, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['content'], self.mock_response['content'])
        self.assertEqual(response.data['message'], '教学大纲生成成功')
        
        # 验证模拟函数被调用
        mock_generate.assert_called_once()
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_teaching_outline_sync')
    def test_teaching_outline_n8n_error(self, mock_generate):
        """测试教学大纲生成API处理n8n错误的情况"""
        # 设置模拟抛出异常
        mock_generate.side_effect = N8nWebhookError("n8n服务暂时不可用")
        
        # 使用教师用户认证
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        response = self.client.post(self.teaching_outline_url, self.valid_payload, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'N8N_WEBHOOK_ERROR')
    
    def test_teaching_outline_validation_error(self):
        """测试教学大纲生成API输入验证错误的情况"""
        # 移除必要字段
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop('knowledge_points')
        
        # 使用教师用户认证
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        response = self.client.post(self.teaching_outline_url, invalid_payload, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_exam_outline_sync')
    def test_exam_outline_success(self, mock_generate):
        """测试考试大纲生成API成功情况"""
        # 设置模拟返回值
        mock_generate.return_value = self.mock_response
        
        # 使用教师用户认证
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        response = self.client.post(self.exam_outline_url, self.valid_payload, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['content'], self.mock_response['content'])
        self.assertEqual(response.data['message'], '考试大纲生成成功')
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_lesson_plan_sync')
    def test_lesson_plan_success(self, mock_generate):
        """测试教案生成API成功情况"""
        # 设置模拟返回值
        mock_generate.return_value = self.mock_response
        
        # 使用教师用户认证
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送请求
        response = self.client.post(self.lesson_plan_url, self.valid_payload, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['content'], self.mock_response['content'])
        self.assertEqual(response.data['message'], '教案生成成功') 