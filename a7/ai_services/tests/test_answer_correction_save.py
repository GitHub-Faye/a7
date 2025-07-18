"""
测试学生答案校正API是否成功将评估结果保存到数据库
"""

import json
from unittest import mock
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, KnowledgePoint, Exercise, StudentAnswer
from ai_services.services.n8n_webhook.client import N8nWebhookClient

User = get_user_model()

class StudentAnswerCorrectionSaveTests(APITestCase):
    """测试学生答案校正API是否成功保存评估结果到数据库"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.student = User.objects.create_user(
            username='teststudent',
            password='testpassword',
            email='student@example.com',
            role='student'
        )
        
        # 创建匿名学生用户（用于测试未登录情况）
        self.anonymous_student = User.objects.create_user(
            username='anonymous_student',
            password='anonymous',
            email='anonymous@example.com',
            role='student'
        )
        
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
    def test_answer_correction_save_authenticated(self, mock_correct_answer):
        """测试已登录用户的答案校正结果保存"""
        # 登录测试用户
        self.client.force_authenticate(user=self.student)
        
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
        
        # 验证数据库中是否保存了学生答案
        self.assertTrue(StudentAnswer.objects.filter(student=self.student, exercise=self.exercise).exists())
        
        saved_answer = StudentAnswer.objects.get(student=self.student, exercise=self.exercise)
        self.assertEqual(saved_answer.content, "B")
        self.assertEqual(saved_answer.score, 100)
        self.assertEqual(saved_answer.is_correct, True)
        self.assertIn("回答正确", saved_answer.feedback)
        self.assertIn("改进建议: 继续保持", saved_answer.feedback)
        self.assertIn("解题思路: 在Python中", saved_answer.feedback)
    
    @mock.patch.object(N8nWebhookClient, 'correct_student_answer_sync')
    def test_answer_correction_save_anonymous(self, mock_correct_answer):
        """测试匿名用户的答案校正结果保存"""
        # 确保未登录
        self.client.logout()
        
        # 模拟AI服务响应
        mock_response = {
            "is_correct": False,
            "score": 0,
            "feedback": "回答错误，1var不是有效的Python变量名",
            "improvement_suggestions": "变量名不能以数字开头",
            "explanation": "在Python中，变量名不能以数字开头，应该以字母或下划线开头"
        }
        mock_correct_answer.return_value = mock_response
        
        # 发送答案校正请求
        data = {
            "exercise_id": self.exercise.id,
            "student_answer": "A",
            "session_id": "test-session-anonymous"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['is_correct'], False)
        self.assertEqual(response.data['data']['score'], 0)
        
        # 验证数据库中是否保存了学生答案，使用匿名学生用户
        self.assertTrue(StudentAnswer.objects.filter(student=self.anonymous_student, exercise=self.exercise).exists())
        
        saved_answer = StudentAnswer.objects.get(student=self.anonymous_student, exercise=self.exercise)
        self.assertEqual(saved_answer.content, "A")
        self.assertEqual(saved_answer.score, 0)
        self.assertEqual(saved_answer.is_correct, False)
        self.assertIn("回答错误", saved_answer.feedback)
    
    @mock.patch.object(N8nWebhookClient, 'correct_student_answer_sync')
    def test_answer_correction_update_existing(self, mock_correct_answer):
        """测试更新已存在的学生答案"""
        # 登录测试用户
        self.client.force_authenticate(user=self.student)
        
        # 创建一个已存在的答案记录
        existing_answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise,
            content="A",
            score=0,
            feedback="回答错误",
            is_correct=False,
            attempt_count=1
        )
        
        # 模拟AI服务响应
        mock_response = {
            "is_correct": True,
            "score": 100,
            "feedback": "回答正确，var1是有效的Python变量名",
            "improvement_suggestions": "继续保持",
            "explanation": "在Python中，变量名不能以数字开头，不能包含特殊字符(除了下划线)，不能包含空格"
        }
        mock_correct_answer.return_value = mock_response
        
        # 发送新的答案校正请求
        data = {
            "exercise_id": self.exercise.id,
            "student_answer": "B",
            "session_id": "test-session-update"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证数据库中的答案记录是否被更新
        updated_answer = StudentAnswer.objects.get(student=self.student, exercise=self.exercise)
        self.assertEqual(updated_answer.content, "B")  # 内容已更新
        self.assertEqual(updated_answer.score, 100)  # 分数已更新
        self.assertEqual(updated_answer.is_correct, True)  # 正确性已更新
        self.assertIn("回答正确", updated_answer.feedback)  # 反馈已更新
        self.assertEqual(updated_answer.attempt_count, 2)  # 尝试次数已增加
    
    def test_answer_correction_no_anonymous_user(self):
        """测试当匿名学生用户不存在时的情况"""
        # 删除匿名学生用户
        self.anonymous_student.delete()
        
        # 确保未登录
        self.client.logout()
        
        # 发送答案校正请求
        data = {
            "exercise_id": self.exercise.id,
            "student_answer": "B",
            "session_id": "test-session-no-anonymous"
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应，应该返回401未授权
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], "AUTHENTICATION_REQUIRED")