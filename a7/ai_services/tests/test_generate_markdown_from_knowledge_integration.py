"""
知识点转Markdown服务(generate_markdown_from_knowledge)与n8n集成测试

此测试文件验证知识点转Markdown服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
"""

import json
import uuid
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Course, KnowledgePoint
from users.models import User
from ai_services.services.n8n_webhook.client import N8nWebhookClient


@pytest.mark.integration  # 标记为集成测试
class GenerateMarkdownFromKnowledgeIntegrationTest(TestCase):
    """知识点转Markdown服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        # 修正URL名称，可能是自定义URL而非视图集
        self.url = reverse('knowledge-to-markdown')  # 修正URL名称，不使用命名空间
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        self.course = Course.objects.create(
            title="Web开发基础", 
            description="学习HTML、CSS和JavaScript的基础知识",
            subject="计算机科学",
            grade_level="大学",
            teacher=self.teacher
        )
        
        # 创建父知识点
        self.parent_knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="HTML基础",
            content="HTML是构建网页的基础，它定义了网页的内容和结构。",
            importance=5
        )
        
        # 创建子知识点
        self.child_knowledge_point1 = KnowledgePoint.objects.create(
            course=self.course,
            parent=self.parent_knowledge_point,
            title="HTML标签",
            content="HTML标签是HTML的基本构建块，用于定义HTML页面中的内容。",
            importance=4
        )
        
        self.child_knowledge_point2 = KnowledgePoint.objects.create(
            course=self.course,
            parent=self.parent_knowledge_point,
            title="HTML属性",
            content="HTML属性提供了有关HTML元素的额外信息。",
            importance=4
        )
        
        # 登录用户
        self.client.force_authenticate(user=self.teacher)
    
    def test_generate_markdown_from_knowledge_api_structure(self):
        """测试知识点转Markdown API的请求和响应结构"""
        # 准备请求数据
        request_data = {
            'knowledge_point_id': self.parent_knowledge_point.id,
            'include_children': True,
            'format_preferences': {
                'include_toc': True,
                'include_examples': True,
                'style': 'academic'
            },
            'session_id': str(uuid.uuid4())
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
        self.assertIn('markdown_content', response_data)
        self.assertIn('session_id', response_data)
        
        # 验证会话ID是否与请求中的相同
        self.assertEqual(response_data['session_id'], request_data['session_id'])
        
        # 验证Markdown内容
        markdown = response_data['markdown_content']
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 0)
        
        # 验证Markdown内容是否包含知识点标题
        self.assertIn(self.parent_knowledge_point.title, markdown)
        
        # 如果include_children为True，验证是否包含子知识点标题
        if request_data['include_children']:
            self.assertIn(self.child_knowledge_point1.title, markdown)
            self.assertIn(self.child_knowledge_point2.title, markdown)
    
    def test_generate_markdown_without_children(self):
        """测试不包含子知识点的Markdown生成"""
        # 准备请求数据
        request_data = {
            'knowledge_point_id': self.parent_knowledge_point.id,
            'include_children': False,
            'session_id': str(uuid.uuid4())
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
        
        # 检查Markdown内容
        markdown = response.data['data']['markdown_content']
        
        # 应包含父知识点内容但不包含子知识点内容
        self.assertIn(self.parent_knowledge_point.title, markdown)
        self.assertNotIn(self.child_knowledge_point1.title, markdown)
        self.assertNotIn(self.child_knowledge_point2.title, markdown)
    
    def test_generate_markdown_invalid_knowledge_point(self):
        """测试使用不存在的知识点ID"""
        # 准备使用不存在的知识点ID的请求数据
        non_existent_id = 9999
        request_data = {
            'knowledge_point_id': non_existent_id,
            'include_children': True,
            'session_id': str(uuid.uuid4())
        }
        
        # 发送请求
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
    
    def test_generate_markdown_error_handling(self):
        """测试知识点转Markdown API的错误处理"""
        # 准备无效的请求数据（缺少必需的knowledge_point_id字段）
        request_data = {
            'include_children': True,
            'session_id': str(uuid.uuid4())
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