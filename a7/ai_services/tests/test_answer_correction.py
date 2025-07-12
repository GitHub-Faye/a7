"""
答案校正功能的测试模块
"""

import json
from unittest import mock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, KnowledgePoint, Exercise
from ai_services.services.n8n_webhook.client import N8nWebhookClient


class StudentAnswerCorrectionTests(APITestCase):
    """测试学生答案校正API"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试数据
        self.course = Course.objects.create(
            title="测试课程",
            description="用于测试的课程",
            subject="计算机科学",
            grade_level="大学"
        )
        
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="Python基础",
            content="Python是一种高级编程语言",
            importance=5
        )
        
        self.exercise = Exercise.objects.create(
            title="Python变量测试",
            content="以下哪个是Python中有效的变量名?",
            type="single_choice",
            difficulty=2,
            knowledge_point=self.knowledge_point,
            answer_template=json.dumps(["1var", "var1", "@var", "var-1"])
        )
        
        # 答案校正API端点
        self.url = reverse('ai_services:correct-answer-list')
        
    @mock.patch.object(N8nWebhookClient, 'correct_student_answer_sync')
    def test_answer_correction(self, mock_correct_answer):
        """测试答案校正功能"""
        # 模拟AI服务响应
        mock_response = {
            "is_correct": True,
            "score": 100,
            "feedback": "回答正确，var1是有效的Python变量名",
            "improvement_suggestions": "继续保持",
            "explanation": "在Python中，变量名不能以数字开头，不能包含特殊字符(除了下划线)，不能包含空格"
        }
        mock_correct_answer.return_value = mock_response
        
        # 发送答案校正请求
        data = {
            "exercise_id": self.exercise.id,
            "student_answer": "B",
            "session_id": "test-session"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['is_correct'], True)
        self.assertEqual(response.data['data']['score'], 100)
        
        # 验证N8nWebhookClient被正确调用
        mock_correct_answer.assert_called_once()
        call_args = mock_correct_answer.call_args[0][0]
        self.assertIn("chatInput", call_args)
        self.assertIn("sessionId", call_args)
        self.assertEqual(call_args["sessionId"], "test-session")
        
        # 验证prompt中包含练习题和学生答案
        prompt = call_args["chatInput"]
        self.assertIn("Python变量测试", prompt)
        self.assertIn("以下哪个是Python中有效的变量名", prompt)
        self.assertIn("学生答案: B", prompt)
    
    def test_answer_correction_invalid_exercise(self):
        """测试使用无效的练习题ID"""
        data = {
            "exercise_id": 9999,  # 不存在的ID
            "student_answer": "这是一个测试答案",
            "session_id": "test-session"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应是错误的
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        # 修改期望，适应实际的响应结构
        self.assertIn("error_code", response.data)
        self.assertEqual(response.data["error_code"], "VALIDATION_ERROR")
    
    def test_answer_correction_missing_fields(self):
        """测试缺少必要字段"""
        # 缺少学生答案
        data = {
            "exercise_id": self.exercise.id,
            "session_id": "test-session"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应是错误的
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        # 修改期望，适应实际的响应结构
        self.assertIn("error_code", response.data)
        self.assertEqual(response.data["error_code"], "VALIDATION_ERROR") 