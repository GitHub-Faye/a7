"""
练习题生成API测试模块
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from courses.models import KnowledgePoint, Course
from users.models import User


class ExerciseGenerationAPITests(TestCase):
    """练习题生成API测试"""

    def setUp(self):
        # 创建测试数据
        self.client = APIClient()
        
        # 创建测试课程和知识点
        self.teacher = User.objects.create_user(username='teacher1', password='password123')
        self.course = Course.objects.create(
            title="测试课程", 
            description="测试课程描述",
            subject="测试学科",
            grade_level="测试年级",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="测试知识点",
            content="测试知识点内容",
            importance=5
        )
        
        # API端点
        self.url = reverse('ai_services:generate-exercises-list')
    
    @patch('ai_services.views.N8nWebhookClient')
    def test_exercise_generation_success(self, mock_client):
        """测试成功生成练习题"""
        # 模拟客户端返回
        mock_instance = mock_client.return_value
        mock_instance.generate_exercises_sync.return_value = {
            "questions": [
                {
                    "title": "测试题目1",
                    "content": "这是一道测试题目",
                    "type": "single_choice",
                    "difficulty": 3,
                    "answer_template": ["选项A", "选项B", "选项C", "选项D"],
                    "knowledge_point_id": self.knowledge_point.id
                }
            ],
            "session_id": "test-session-id"
        }
        
        # 发送请求
        data = {
            "query": "测试题目生成",
            "knowledge_point_ids": [self.knowledge_point.id],
            "quantity": 1
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['exercises']), 1)
        self.assertIn('session_id', response.data['data'])
        
        # 验证调用
        mock_instance.generate_exercises_sync.assert_called_once()
        call_args = mock_instance.generate_exercises_sync.call_args[0][0]
        self.assertEqual(call_args['query'], "测试题目生成")
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_exercise_generation_error(self, mock_client):
        """测试生成练习题失败的情况"""
        # 模拟客户端抛出异常
        from ai_services.services.n8n_webhook.exceptions import N8nWebhookError
        mock_instance = mock_client.return_value
        mock_instance.generate_exercises_sync.side_effect = N8nWebhookError("测试错误")
        
        # 发送请求
        data = {"query": "测试题目生成"}
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], "N8N_WEBHOOK_ERROR")
        
    def test_exercise_generation_invalid_params(self):
        """测试无效参数情况"""
        # 发送请求 - 缺少必需参数
        response = self.client.post(self.url, {}, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], "VALIDATION_ERROR")
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_exercise_generation_with_all_options(self, mock_client):
        """测试使用所有选项生成练习题"""
        # 模拟客户端返回
        mock_instance = mock_client.return_value
        mock_instance.generate_exercises_sync.return_value = {
            "questions": [
                {
                    "title": "测试题目1",
                    "content": "这是一道测试题目",
                    "type": "single_choice",
                    "difficulty": 4,
                    "answer_template": ["选项A", "选项B", "选项C", "选项D"],
                    "knowledge_point_id": self.knowledge_point.id
                },
                {
                    "title": "测试题目2",
                    "content": "这是另一道测试题目",
                    "type": "multiple_choice",
                    "difficulty": 4,
                    "answer_template": ["选项A", "选项B", "选项C", "选项D"],
                    "knowledge_point_id": self.knowledge_point.id
                }
            ],
            "session_id": "test-session-id-2"
        }
        
        # 发送请求 - 包含所有选项
        data = {
            "query": "测试题目生成",
            "knowledge_point_ids": [self.knowledge_point.id],
            "question_types": ["single_choice", "multiple_choice"],
            "quantity": 2,
            "difficulty": 4,
            "session_id": "test-session-id-2"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['exercises']), 2)
        self.assertEqual(response.data['data']['session_id'], "test-session-id-2")
        
        # 验证调用参数
        call_args = mock_instance.generate_exercises_sync.call_args[0][0]
        self.assertEqual(call_args['query'], "测试题目生成")
        self.assertEqual(call_args['quantity'], 2)
        self.assertEqual(call_args['difficulty'], 4)
        self.assertEqual(call_args['sessionId'], "test-session-id-2")
        self.assertEqual(call_args['question_types'], ["single_choice", "multiple_choice"])
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_exercise_generation_anonymous_access(self, mock_client):
        """测试匿名访问API"""
        # 确保客户端未认证
        self.client.logout()
        
        # 模拟客户端返回
        mock_instance = mock_client.return_value
        mock_instance.generate_exercises_sync.return_value = {
            "questions": [
                {
                    "title": "匿名测试题目",
                    "content": "这是一道匿名用户生成的测试题目",
                    "type": "short_answer",
                    "difficulty": 3,
                    "answer_template": "参考答案",
                    "knowledge_point_id": None
                }
            ],
            "session_id": "anonymous-session"
        }
        
        # 发送请求
        data = {"query": "匿名测试题目生成"}
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应 - 匿名用户应该能成功访问
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['exercises']), 1) 