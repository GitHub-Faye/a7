"""
问题导出功能测试
"""

import json
import csv
from io import StringIO
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from users.models import User, Role
from courses.models import Course, KnowledgePoint
from ai_services.services.question_export import QuestionExporter

class QuestionExportToolTests(TestCase):
    """问题导出工具类测试"""
    
    def setUp(self):
        """测试前准备"""
        # 准备测试数据
        self.test_questions = [
            {
                "title": "Python基础概念",
                "content": "什么是Python的动态类型系统？",
                "type": "short_answer",
                "difficulty": 3,
                "answer_template": "Python是动态类型语言，意味着变量类型在运行时确定而非编译时...",
                "knowledge_point_id": 1
            },
            {
                "title": "数据结构选择",
                "content": "以下哪个数据结构适合用于实现先进先出队列？",
                "type": "single_choice",
                "difficulty": 2,
                "answer_template": ["队列", "栈", "哈希表", "集合"],
                "knowledge_point_id": 2
            }
        ]
    
    def test_export_as_json(self):
        """测试JSON格式导出"""
        response = QuestionExporter.export_as_json(self.test_questions)
        
        # 检查响应类型
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
        
        # 检查响应内容
        content = json.loads(response.content.decode('utf-8'))
        self.assertIn('questions', content)
        self.assertEqual(len(content['questions']), 2)
        self.assertEqual(content['questions'][0]['title'], "Python基础概念")
        
    def test_export_as_csv(self):
        """测试CSV格式导出"""
        response = QuestionExporter.export_as_csv(self.test_questions)
        
        # 检查响应类型
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
        
        # 检查响应内容
        # 先去除BOM标记
        content = response.content.decode('utf-8-sig')
        
        # 使用CSV读取器解析内容
        reader = csv.reader(StringIO(content))
        rows = list(reader)
        
        # 检查表头
        self.assertEqual(len(rows), 3)  # 表头 + 2行数据
        self.assertIn('title', rows[0])
        self.assertIn('content', rows[0])
        self.assertIn('type', rows[0])
        
        # 检查数据行
        self.assertIn('Python基础概念', rows[1])
        self.assertIn('short_answer', rows[1])
        
    def test_export_questions_json(self):
        """测试通用导出方法 - JSON格式"""
        response = QuestionExporter.export_questions(
            self.test_questions, 
            format_type='json',
            filename='test_export'
        )
        
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        self.assertIn('attachment; filename="test_export.json"', response['Content-Disposition'])
        
    def test_export_questions_csv(self):
        """测试通用导出方法 - CSV格式"""
        response = QuestionExporter.export_questions(
            self.test_questions, 
            format_type='csv',
            filename='test_export'
        )
        
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn('attachment; filename="test_export.csv"', response['Content-Disposition'])
        
    def test_export_invalid_format(self):
        """测试不支持的导出格式"""
        with self.assertRaises(ValueError):
            QuestionExporter.export_questions(
                self.test_questions, 
                format_type='xml'  # 不支持的格式
            )

class QuestionExportAPITests(TestCase):
    """问题导出API测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建用户
        self.admin_user = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.teacher_user = User.objects.create_user(username='teacher', password='teacher123')
        
        # 设置角色
        admin_role = Role.objects.get_or_create(name='admin')[0]
        teacher_role = Role.objects.get_or_create(name='teacher')[0]
        
        self.admin_user.role = admin_role
        self.teacher_user.role = teacher_role
        
        self.admin_user.save()
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
        
        # 准备测试数据
        self.test_questions = [
            {
                "title": "Python基础概念",
                "content": "什么是Python的动态类型系统？",
                "type": "short_answer",
                "difficulty": 3,
                "answer_template": "Python是动态类型语言，意味着变量类型在运行时确定而非编译时...",
                "knowledge_point_id": self.kp1.id
            }
        ]
        
        # 创建客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.teacher_user)
        
        # 创建测试会话键
        self.session_key = 'test_session_key'
        
        # 创建请求工厂
        self.factory = RequestFactory()
    
    def test_export_endpoint(self):
        """测试导出端点"""
        # 模拟会话数据
        request = self.factory.get('/api/questions-generate/export/')
        request.user = self.teacher_user
        request.session = {
            self.session_key: {
                'questions': self.test_questions,
                'created_at': '2023-01-01T00:00:00',
                'knowledge_point_ids': [self.kp1.id],
                'question_types': ['short_answer']
            }
        }
        
        # 模拟导出工具
        with patch('ai_services.services.question_export.QuestionExporter.export_questions') as mock_export:
            # 模拟导出工具返回的响应
            mock_response = HttpResponse(content_type='application/json')
            mock_response['Content-Disposition'] = 'attachment; filename="test.json"'
            mock_export.return_value = mock_response
            
            # 发送请求
            from courses.views import QuestionGenerationViewSet
            view = QuestionGenerationViewSet()
            view.request = request
            view.format_kwarg = None
            
            # 添加查询参数
            request.query_params = {
                'session_key': self.session_key,
                'format': 'json'
            }
            
            # 调用导出方法
            response = view.export(request)
            
            # 验证导出工具被正确调用
            mock_export.assert_called_once()
            
    def test_export_missing_session_key(self):
        """测试缺少会话键的情况"""
        response = self.client.get('/api/questions-generate/export/')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'MISSING_PARAMETER')
        
    def test_export_invalid_session_key(self):
        """测试无效会话键的情况"""
        response = self.client.get('/api/questions-generate/export/?session_key=invalid_key')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'NOT_FOUND')
        
    def test_export_invalid_format(self):
        """测试无效导出格式的情况"""
        # 模拟会话数据
        request = self.factory.get(f'/api/questions-generate/export/?session_key={self.session_key}&format=xml')
        request.user = self.teacher_user
        request.session = {
            self.session_key: {
                'questions': self.test_questions,
                'created_at': '2023-01-01T00:00:00'
            }
        }
        
        # 发送请求
        from courses.views import QuestionGenerationViewSet
        view = QuestionGenerationViewSet()
        view.request = request
        view.format_kwarg = None
        
        # 添加查询参数
        request.query_params = {
            'session_key': self.session_key,
            'format': 'xml'  # 无效格式
        }
        
        # 调用导出方法
        response = view.export(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'INVALID_FORMAT') 