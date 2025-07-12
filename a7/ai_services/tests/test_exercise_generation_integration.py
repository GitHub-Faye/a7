"""
练习题生成API集成测试模块

此测试模块包含与真实N8N服务集成的测试，将调用实际的AI服务生成练习题。
注意：运行此测试需要配置有效的N8N服务连接。
"""

import os
import uuid
from django.test import TestCase, tag
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import KnowledgePoint, Course
from users.models import User
from ai_services.services.n8n_webhook.client import N8nWebhookClient


@tag('integration')  # 使用标签标记为集成测试，可以单独运行或排除
class ExerciseGenerationIntegrationTests(TestCase):
    """练习题生成API与实际N8N服务的集成测试"""

    def setUp(self):
        """设置测试环境"""
        # 检查是否配置了N8N服务
        self.n8n_url = os.environ.get('N8N_WEBHOOK_URL')
        if not self.n8n_url:
            self.skipTest("未配置N8N_WEBHOOK_URL环境变量，跳过集成测试")
            
        # 创建测试数据
        self.client = APIClient()
        
        # 创建测试课程和知识点
        self.teacher = User.objects.create_user(username='teacher_integration', password='password123')
        self.course = Course.objects.create(
            title="Python编程基础", 
            description="Python编程语言入门课程",
            subject="计算机科学",
            grade_level="大学一年级",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="Python变量和数据类型",
            content="Python中的变量不需要声明类型，可以直接赋值使用。Python的基本数据类型包括：整数(int)、浮点数(float)、字符串(str)、布尔值(bool)等。",
            importance=5
        )
        
        # API端点
        self.url = reverse('ai_services:generate-exercises-list')
    
    @tag('slow')  # 标记为慢速测试
    def test_real_exercise_generation(self):
        """测试使用真实N8N服务生成练习题"""
        # 准备请求数据
        data = {
            "query": "Python变量和数据类型",
            "knowledge_point_ids": [self.knowledge_point.id],
            "question_types": ["single_choice", "multiple_choice", "short_answer"],
            "quantity": 2,
            "difficulty": 3,
            "session_id": str(uuid.uuid4())
        }
        
        try:
            # 直接发送请求到API
            response = self.client.post(self.url, data, format='json')
            
            # 验证响应状态码
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            
            # 验证返回的练习题
            exercises = response.data['data']['exercises']
            self.assertIsNotNone(exercises)
            self.assertGreaterEqual(len(exercises), 1)  # 应至少返回1道题
            
            # 验证练习题结构
            for exercise in exercises:
                self.assertIn('title', exercise)
                self.assertIn('content', exercise)
                self.assertIn('type', exercise)
                self.assertIn(exercise['type'], ["single_choice", "multiple_choice", "short_answer"])
                
                # 根据题型验证答案模板
                if exercise['type'] in ['single_choice', 'multiple_choice']:
                    self.assertIn('answer_template', exercise)
                    self.assertIsInstance(exercise['answer_template'], list)
                    
            # 验证会话ID
            self.assertIn('session_id', response.data['data'])
            
            print(f"成功生成了{len(exercises)}道练习题")
            
        except Exception as e:
            self.fail(f"集成测试失败: {str(e)}")
    
    def test_direct_client_call(self):
        """直接测试N8nWebhookClient的练习题生成方法"""
        try:
            # 创建客户端实例
            client = N8nWebhookClient()
            
            # 准备请求数据
            request_data = {
                "query": "Python列表和元组的区别",
                "knowledge_content": "Python中的列表(list)是可变的，而元组(tuple)是不可变的。列表使用方括号[]，元组使用圆括号()。",
                "question_types": ["short_answer"],
                "quantity": 1,
                "difficulty": 3,
                "chatInput": "生成1道关于Python列表和元组区别的简答题",
                "sessionId": str(uuid.uuid4())
            }
            
            # 直接调用客户端方法
            result = client.generate_exercises_sync(request_data)
            
            # 验证结果
            self.assertIn('questions', result)
            self.assertGreaterEqual(len(result['questions']), 1)
            
            print(f"N8nWebhookClient直接调用成功生成了{len(result['questions'])}道练习题")
            
        except Exception as e:
            self.fail(f"直接客户端调用测试失败: {str(e)}") 