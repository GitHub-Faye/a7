"""
问题生成和导出集成测试
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch, MagicMock
from users.models import User, Role
from courses.models import Course, KnowledgePoint
from ai_services.services.n8n_webhook.formats import QuestionGenerationResponseData

class QuestionGenerationExportIntegrationTests(TestCase):
    """问题生成和导出集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建用户
        self.teacher_user = User.objects.create_user(username='teacher', password='teacher123')
        
        # 设置角色
        teacher_role = Role.objects.get_or_create(name='teacher')[0]
        self.teacher_user.role = teacher_role
        self.teacher_user.save()
        
        # 创建课程
        self.course = Course.objects.create(
            title='测试课程',
            description='测试课程描述',
            subject='计算机科学',
            grade_level='大学',
            teacher=self.teacher_user
        )
        
        # 创建知识点
        self.kp1 = KnowledgePoint.objects.create(
            course=self.course,
            title='Python基础',
            content='Python是一种高级编程语言，以其简洁、易读的语法著称。',
            importance=8
        )
        
        # 创建客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.teacher_user)
        
        # 准备请求数据
        self.generate_data = {
            'knowledge_point_ids': [self.kp1.id],
            'question_types': ['short_answer', 'single_choice'],
            'quantity': 2,
            'difficulty': 3
        }
        
        # 模拟生成的问题
        self.mock_questions = [
            {
                "title": "Python基础概念",
                "content": "什么是Python的动态类型系统？",
                "type": "short_answer",
                "difficulty": 3,
                "answer_template": "Python是动态类型语言，意味着变量类型在运行时确定而非编译时...",
                "knowledge_point_id": self.kp1.id
            },
            {
                "title": "Python数据结构",
                "content": "以下哪个不是Python的内置数据结构？",
                "type": "single_choice",
                "difficulty": 3,
                "answer_template": ["LinkedList", "List", "Dictionary", "Set"],
                "knowledge_point_id": self.kp1.id
            }
        ]
        
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.generate_questions_sync')
    def test_generate_and_export_flow(self, mock_generate):
        """测试完整的问题生成和导出流程"""
        # 1. 模拟AI问题生成响应
        mock_generate.return_value = {
            'questions': self.mock_questions
        }
        
        # 2. 发送问题生成请求
        response = self.client.post(
            reverse('questions-generate-list'),
            data=self.generate_data,
            format='json'
        )
        
        # 检查响应状态和数据
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['success'])
        self.assertIn('questions', response.data['data'])
        self.assertIn('session_key', response.data['data'])
        
        # 获取会话键
        session_key = response.data['data']['session_key']
        
        # 3. 准备导出环境
        from django.test import RequestFactory
        from courses.views import QuestionGenerationViewSet
        factory = RequestFactory()
        
        # 4. 导出为JSON格式
        with patch('ai_services.services.question_export.QuestionExporter.export_questions') as mock_export:
            # 创建请求和视图
            request = factory.get(f'/api/questions-generate/export/?session_key={session_key}&format=json')
            request.user = self.teacher_user
            # 模拟会话
            request.session = {
                session_key: {
                    'questions': self.mock_questions,
                    'created_at': '2023-01-01T00:00:00'
                }
            }
            
            # 模拟响应
            from django.http import HttpResponse
            mock_response = HttpResponse(
                json.dumps({'questions': self.mock_questions}),
                content_type='application/json'
            )
            mock_response['Content-Disposition'] = 'attachment; filename="test.json"'
            mock_export.return_value = mock_response
            
            # 创建视图
            view = QuestionGenerationViewSet()
            view.request = request
            view.format_kwarg = None
            
            # 添加查询参数
            request.query_params = {
                'session_key': session_key,
                'format': 'json'
            }
            
            # 调用导出方法
            response = view.export(request)
            
            # 检查导出响应
            self.assertEqual(response.status_code, 200)
            mock_export.assert_called_once()
            args, kwargs = mock_export.call_args
            self.assertEqual(kwargs['questions'], self.mock_questions)
            self.assertEqual(kwargs['format_type'], 'json')
        
        # 5. 测试导出为CSV格式
        with patch('ai_services.services.question_export.QuestionExporter.export_questions') as mock_export:
            # 创建请求和视图
            request = factory.get(f'/api/questions-generate/export/?session_key={session_key}&format=csv')
            request.user = self.teacher_user
            # 模拟会话
            request.session = {
                session_key: {
                    'questions': self.mock_questions,
                    'created_at': '2023-01-01T00:00:00'
                }
            }
            
            # 模拟响应
            from django.http import HttpResponse
            mock_response = HttpResponse(
                content='id,title,content,type,difficulty,knowledge_point_id,answer_template\n',
                content_type='text/csv'
            )
            mock_response['Content-Disposition'] = 'attachment; filename="test.csv"'
            mock_export.return_value = mock_response
            
            # 创建视图
            view = QuestionGenerationViewSet()
            view.request = request
            view.format_kwarg = None
            
            # 添加查询参数
            request.query_params = {
                'session_key': session_key,
                'format': 'csv'
            }
            
            # 调用导出方法
            response = view.export(request)
            
            # 检查导出响应
            self.assertEqual(response.status_code, 200)
            mock_export.assert_called_once()
            args, kwargs = mock_export.call_args
            self.assertEqual(kwargs['questions'], self.mock_questions)
            self.assertEqual(kwargs['format_type'], 'csv') 