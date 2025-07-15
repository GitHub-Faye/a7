"""
答案校正服务(correct_student_answer)与n8n集成测试

此测试文件验证答案校正服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
"""

import json
import uuid
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Course, KnowledgePoint, Exercise
from users.models import User
from ai_services.services.n8n_webhook.client import N8nWebhookClient


@pytest.mark.integration  # 标记为集成测试
class CorrectStudentAnswerIntegrationTest(TestCase):
    """答案校正服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('ai_services:correct-answer-list')  # 基于视图集的URL名称
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        self.course = Course.objects.create(
            title="编程基础", 
            description="Python编程入门",
            subject="计算机科学",
            grade_level="大学",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="Python循环语句",
            content="Python中的循环结构包括for循环和while循环，用于重复执行特定的代码块。",
            importance=5
        )
        
        # 创建不同类型的练习题
        self.single_choice_exercise = Exercise.objects.create(
            title="Python循环选择",
            content="以下哪个循环最适合遍历一个列表？",
            type="single_choice",
            difficulty=2,
            knowledge_point=self.knowledge_point,
            answer_template=json.dumps(["while循环", "for循环", "do-while循环", "repeat-until循环"])
        )
        
        self.short_answer_exercise = Exercise.objects.create(
            title="Python循环解释",
            content="简述for循环和while循环的主要区别。",
            type="short_answer",
            difficulty=3,
            knowledge_point=self.knowledge_point
        )
        
        # 存储参考答案，供直接API测试使用
        self.single_choice_reference = "B"
        self.short_answer_reference = "for循环通常用于已知迭代次数的情况，适合遍历集合；while循环通常用于未知迭代次数的情况，基于条件判断是否继续执行。"
    
    def test_correct_single_choice_answer(self):
        """测试单选题答案校正API的请求和响应结构"""
        # 准备请求数据 - 需要传递exercise_id和reference_answer
        session_id = str(uuid.uuid4())
        request_data = {
            'exercise_id': self.single_choice_exercise.id,
            'student_answer': 'B',
            'reference_answer': self.single_choice_reference,
            'session_id': session_id
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
        self.assertIn('is_correct', response_data)
        self.assertIn('score', response_data)
        self.assertIn('feedback', response_data)
        self.assertIn('improvement_suggestions', response_data)
        self.assertIn('session_id', response_data)
        
        # 验证会话ID是否与请求中的相同
        self.assertEqual(response_data['session_id'], session_id)
        
        # 验证答案评分结果
        self.assertIsInstance(response_data['is_correct'], bool)
        self.assertIsInstance(response_data['score'], (int, float))
        self.assertGreaterEqual(response_data['score'], 0)
        self.assertLessEqual(response_data['score'], 100)
    
    def test_correct_short_answer(self):
        """测试简答题答案校正API的请求和响应结构"""
        # 准备请求数据
        session_id = str(uuid.uuid4())
        request_data = {
            'exercise_id': self.short_answer_exercise.id,
            'student_answer': 'for循环用于遍历列表等序列，while循环用于条件判断循环。',
            'reference_answer': self.short_answer_reference,
            'session_id': session_id
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
        self.assertIn('is_correct', response_data)
        self.assertIn('score', response_data)
        self.assertIn('feedback', response_data)
        
        # 验证评分结果
        self.assertIsInstance(response_data['score'], (int, float))
        self.assertGreaterEqual(response_data['score'], 0)
        self.assertLessEqual(response_data['score'], 100)
    
    def test_correct_answer_error_handling(self):
        """测试答案校正API的错误处理"""
        # 准备无效的请求数据（缺少必需字段）
        request_data = {
            'student_answer': 'B'
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
        
    # 可以添加直接针对客户端的测试，测试原始参数传递方式
    def test_client_direct_call(self):
        """测试直接调用客户端方法并传递原始参数"""
        client = N8nWebhookClient()
        session_id = str(uuid.uuid4())
        
        # 为单选题准备测试数据
        single_choice_data = {
            "exercise_content": self.single_choice_exercise.content,
            "exercise_type": self.single_choice_exercise.type,
            "reference_answer": self.single_choice_reference,
            "student_answer": "B",
            "answer_template": json.loads(self.single_choice_exercise.answer_template),
            "sessionId": session_id
        }
        
        # 模拟测试，不实际调用API
        # 这里可以添加mock对象和断言来验证参数是否正确传递
        # 暂时跳过实际调用，因为n8n可能不在测试环境中可用
        # result = client.correct_student_answer_sync(single_choice_data)
        # self.assertIn('is_correct', result)
        # self.assertTrue(result['is_correct']) 