"""
答案校正功能的集成测试模块

此测试使用真实的n8n服务，验证整个答案校正流程
"""

import json
import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, KnowledgePoint, Exercise
from ai_services.services.n8n_webhook.client import N8nWebhookClient


class StudentAnswerCorrectionIntegrationTests(APITestCase):
    """测试学生答案校正API的集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试数据
        self.course = Course.objects.create(
            title="Python编程基础",
            description="Python编程语言入门课程",
            subject="计算机科学",
            grade_level="大学"
        )
        
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="Python变量与数据类型",
            content="Python中的变量命名规则和基本数据类型",
            importance=5
        )
        
        # 创建单选题
        self.single_choice_exercise = Exercise.objects.create(
            title="Python变量命名规则",
            content="以下哪个是Python中有效的变量名?",
            type="single_choice",
            difficulty=2,
            knowledge_point=self.knowledge_point,
            answer_template=json.dumps(["1var", "var1", "@var", "var-1"])
        )
        
        # 创建多选题
        self.multiple_choice_exercise = Exercise.objects.create(
            title="Python数据类型",
            content="以下哪些是Python的基本数据类型? (选择所有正确答案)",
            type="multiple_choice",
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template=json.dumps(["int", "boolean", "char", "float", "string"])
        )
        
        # 创建简答题
        self.short_answer_exercise = Exercise.objects.create(
            title="Python变量特点",
            content="简述Python变量的特点及其与其他编程语言变量的区别。",
            type="short_answer",
            difficulty=4,
            knowledge_point=self.knowledge_point,
            answer_template="Python变量是动态类型，不需要预先声明类型，可以随时改变类型。Python变量实际上是对象的引用。"
        )
        
        # 答案校正API端点
        self.url = reverse('ai_services:correct-answer-list')
        
    def test_single_choice_answer_correction(self):
        """测试单选题答案校正功能"""
        # 跳过测试，如果环境变量指示跳过集成测试
        import os
        if os.environ.get('SKIP_INTEGRATION_TESTS') == 'true':
            self.skipTest("跳过集成测试")
            
        # 发送正确答案
        data = {
            "exercise_id": self.single_choice_exercise.id,
            "student_answer": "B",  # var1是正确答案
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果
        result = response.data['data']
        self.assertIn('is_correct', result)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        
        # 预期这个答案是正确的
        self.assertTrue(result['is_correct'])
        self.assertGreaterEqual(result['score'], 80)  # 分数应该很高
        
        # 发送错误答案
        data = {
            "exercise_id": self.single_choice_exercise.id,
            "student_answer": "A",  # 1var是错误答案
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果
        result = response.data['data']
        self.assertIn('is_correct', result)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        
        # 预期这个答案是错误的
        self.assertFalse(result['is_correct'])
        self.assertLessEqual(result['score'], 50)  # 分数应该很低
    
    def test_short_answer_correction(self):
        """测试简答题答案校正功能"""
        # 跳过测试，如果环境变量指示跳过集成测试
        import os
        if os.environ.get('SKIP_INTEGRATION_TESTS') == 'true':
            self.skipTest("跳过集成测试")
            
        # 发送一个好的答案
        data = {
            "exercise_id": self.short_answer_exercise.id,
            "student_answer": "Python变量是动态类型的，不需要预先声明变量类型。Python变量实际上是引用，指向内存中的对象。与静态类型语言不同，Python变量可以随时改变类型。",
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果
        result = response.data['data']
        self.assertIn('is_correct', result)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        self.assertIn('explanation', result)
        
        # 预期这个答案得分较高
        self.assertGreaterEqual(result['score'], 70)
        
        # 发送一个不完整的答案
        data = {
            "exercise_id": self.short_answer_exercise.id,
            "student_answer": "Python变量不需要声明类型。",
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果
        result = response.data['data']
        
        # 预期这个答案得分较低
        self.assertLessEqual(result['score'], 60)
        self.assertIn('improvement_suggestions', result)  # 应该有改进建议 
    
    def test_multiple_choice_correction(self):
        """测试多选题答案校正功能"""
        # 跳过测试，如果环境变量指示跳过集成测试
        import os
        if os.environ.get('SKIP_INTEGRATION_TESTS') == 'true':
            self.skipTest("跳过集成测试")
            
        # 发送一个答案
        data = {
            "exercise_id": self.multiple_choice_exercise.id,
            "student_answer": "A,D,E",  # int, float, string
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果格式
        result = response.data['data']
        self.assertIn('is_correct', result)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        
        # 验证分数在合理范围内
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        
        # 发送另一个答案
        data = {
            "exercise_id": self.multiple_choice_exercise.id,
            "student_answer": "A,B,D",  # int, boolean, float
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果格式
        result = response.data['data']
        self.assertIn('is_correct', result)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        
        # 验证分数在合理范围内
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100) 
    
    def test_multiple_choice_correction_alternative(self):
        """测试多选题答案校正功能 - 另一个答案"""
        # 跳过测试，如果环境变量指示跳过集成测试
        import os
        if os.environ.get('SKIP_INTEGRATION_TESTS') == 'true':
            self.skipTest("跳过集成测试")
            
        # 发送另一个答案
        data = {
            "exercise_id": self.multiple_choice_exercise.id,
            "student_answer": "A,B,D",  # int, boolean, float
            "session_id": str(uuid.uuid4())
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证评估结果
        result = response.data['data']
        
        # 验证所有必要字段存在
        self.assertIn('is_correct', result)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        
        # 分数应该在合理范围内
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100) 