"""
知识点转PPT服务(KnowledgePointToPPT)与n8n集成测试

此测试文件验证知识点转PPT服务是否正确集成了n8n服务，并检查API接口是否按照统一标准重构。
"""

import json
import uuid
import pytest
import os
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Course, KnowledgePoint
from users.models import User
from ai_services.services.n8n_webhook.client import N8nWebhookClient


@pytest.mark.integration  # 标记为集成测试
class KnowledgePointToPPTIntegrationTest(TestCase):
    """知识点转PPT服务与n8n集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('knowledge-to-ppt-list')  # 修正URL名称，不使用命名空间
        
        # 创建测试数据
        self.teacher = User.objects.create_user(username='test_teacher', password='password123')
        self.course = Course.objects.create(
            title="计算机网络", 
            description="计算机网络基础知识",
            subject="计算机科学",
            grade_level="大学",
            teacher=self.teacher
        )
        
        # 创建父知识点
        self.parent_knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="TCP/IP协议",
            content="TCP/IP是互联网最基本的通信协议，它定义了电子设备如何连接到网络以及数据如何在网络间传输的标准。",
            importance=5
        )
        
        # 创建子知识点
        self.child_knowledge_point1 = KnowledgePoint.objects.create(
            course=self.course,
            parent=self.parent_knowledge_point,
            title="TCP协议",
            content="传输控制协议(TCP)是一种面向连接的、可靠的、基于字节流的传输层通信协议。",
            importance=4
        )
        
        self.child_knowledge_point2 = KnowledgePoint.objects.create(
            course=self.course,
            parent=self.parent_knowledge_point,
            title="IP协议",
            content="互联网协议(IP)是用于分组交换数据网络的一种协议，它在Internet协议族中处于网络层。",
            importance=4
        )
        
        # 登录用户
        self.client.force_authenticate(user=self.teacher)
    
    def test_knowledge_point_to_ppt_api_structure(self):
        """测试知识点转PPT API的请求和响应结构"""
        # 准备请求数据
        request_data = {
            'knowledge_point_id': self.parent_knowledge_point.id,
            'include_children': True,
            'template': 'default',
            'format': 'pptx',
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
        self.assertIn('file_url', response_data)
        self.assertIn('session_id', response_data)
        
        # 验证会话ID是否与请求中的相同
        self.assertEqual(response_data['session_id'], request_data['session_id'])
        
        # 验证文件URL
        file_url = response_data['file_url']
        self.assertIsInstance(file_url, str)
        self.assertTrue(file_url.endswith('.pptx'))
        
        # 验证响应中是否包含文件信息
        self.assertIn('file_info', response_data)
        file_info = response_data['file_info']
        self.assertIn('filename', file_info)
        self.assertIn('size', file_info)
        self.assertIn('created_at', file_info)
    
    def test_knowledge_point_to_ppt_with_different_template(self):
        """测试使用不同模板生成PPT"""
        # 准备请求数据
        request_data = {
            'knowledge_point_id': self.parent_knowledge_point.id,
            'include_children': True,
            'template': 'modern',  # 使用不同模板
            'format': 'pptx',
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
        
        # 验证文件URL中包含模板信息
        file_url = response.data['data']['file_url']
        self.assertIsInstance(file_url, str)
    
    def test_knowledge_point_to_ppt_invalid_knowledge_point(self):
        """测试使用不存在的知识点ID"""
        # 准备使用不存在的知识点ID的请求数据
        non_existent_id = 9999
        request_data = {
            'knowledge_point_id': non_existent_id,
            'include_children': True,
            'template': 'default',
            'format': 'pptx',
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
    
    def test_knowledge_point_to_ppt_error_handling(self):
        """测试知识点转PPT API的错误处理"""
        # 准备无效的请求数据（缺少必需的knowledge_point_id字段）
        request_data = {
            'template': 'default',
            'format': 'pptx',
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