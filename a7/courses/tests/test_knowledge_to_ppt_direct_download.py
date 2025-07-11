import os
import shutil
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APIClient
from rest_framework import status

from courses.models import Course, KnowledgePoint
from courses.serializers_ppt import KnowledgePointToPPTSerializer
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService

User = get_user_model()

# 创建测试媒体目录
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'test_media')
TEST_PRESENTATION_DIR = os.path.join(TEST_MEDIA_ROOT, 'presentations')

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class KnowledgePointToPPTDirectDownloadTests(TestCase):
    """测试知识点到PPT的直接下载功能"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            subject='测试学科',
            grade_level='测试年级',
            teacher=self.user
        )
        
        # 创建测试知识点
        self.kp = KnowledgePoint.objects.create(
            title='测试知识点',
            content='测试内容',
            course=self.course,
            importance=5
        )
        
        # 确保测试媒体目录存在
        os.makedirs(TEST_PRESENTATION_DIR, exist_ok=True)
        
        # 创建一个测试文件
        self.test_file_path = os.path.join(TEST_PRESENTATION_DIR, 'test_presentation.pptx')
        with open(self.test_file_path, 'wb') as f:
            f.write(b'Test PPTX content')
        
        # 创建API客户端
        self.client = APIClient()
        
        # 获取API URL
        self.url = reverse('knowledge-points-to-ppt-list')
    
    def tearDown(self):
        # 清理测试媒体目录
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)
    
    @patch('courses.services.knowledge_to_ppt.KnowledgePointToPPTService.process_knowledge_points_to_ppt')
    def test_direct_download_response(self, mock_process):
        """测试直接下载选项返回正确的响应类型和头信息"""
        # 设置mock返回值
        file_path_rel = 'presentations/test_presentation.pptx'
        mock_process.return_value = {
            "status": "success",
            "data": {
                "file_url": f"/media/{file_path_rel}",
                "filename": "test_presentation.pptx"
            }
        }
        
        # 准备请求数据
        data = {
            "knowledge_point_ids": [self.kp.id],
            "format": "pptx",
            "direct_download": True
        }
        
        # 发送请求
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="test_presentation.pptx"')
        self.assertEqual(response.content, b'Test PPTX content')
    
    @patch('courses.services.knowledge_to_ppt.KnowledgePointToPPTService.process_knowledge_points_to_ppt')
    def test_custom_filename(self, mock_process):
        """测试自定义文件名功能"""
        # 设置mock返回值
        file_path_rel = 'presentations/test_presentation.pptx'
        mock_process.return_value = {
            "status": "success",
            "data": {
                "file_url": f"/media/{file_path_rel}",
                "filename": "test_presentation.pptx"
            }
        }
        
        # 准备请求数据，包括自定义文件名
        data = {
            "knowledge_point_ids": [self.kp.id],
            "format": "pptx",
            "direct_download": True,
            "filename": "custom_name"
        }
        
        # 发送请求
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="custom_name.pptx"')
    
    @patch('courses.services.knowledge_to_ppt.KnowledgePointToPPTService.process_knowledge_points_to_ppt')
    def test_content_type_by_format(self, mock_process):
        """测试不同格式的Content-Type设置"""
        # 创建不同格式的测试文件
        test_pdf_path = os.path.join(TEST_PRESENTATION_DIR, 'test_presentation.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(b'Test PDF content')
            
        test_html_path = os.path.join(TEST_PRESENTATION_DIR, 'test_presentation.html')
        with open(test_html_path, 'wb') as f:
            f.write(b'<html><body>Test HTML content</body></html>')
        
        # 测试PDF格式
        mock_process.return_value = {
            "status": "success",
            "data": {
                "file_url": "/media/presentations/test_presentation.pdf",
                "filename": "test_presentation.pdf"
            }
        }
        
        data = {
            "knowledge_point_ids": [self.kp.id],
            "format": "pdf",
            "direct_download": True
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # 测试HTML格式
        mock_process.return_value = {
            "status": "success",
            "data": {
                "file_url": "/media/presentations/test_presentation.html",
                "filename": "test_presentation.html"
            }
        }
        
        data = {
            "knowledge_point_ids": [self.kp.id],
            "format": "html",
            "direct_download": True
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html')
    
    @patch('courses.services.knowledge_to_ppt.KnowledgePointToPPTService.process_knowledge_points_to_ppt')
    def test_file_not_found(self, mock_process):
        """测试文件不存在的情况"""
        # 设置mock返回值，但文件不存在
        mock_process.return_value = {
            "status": "success",
            "data": {
                "file_url": "/media/presentations/nonexistent_file.pptx",
                "filename": "nonexistent_file.pptx"
            }
        }
        
        # 准备请求数据
        data = {
            "knowledge_point_ids": [self.kp.id],
            "format": "pptx",
            "direct_download": True
        }
        
        # 发送请求
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, 404)
        # 验证响应内容符合中间件修改后的格式
        self.assertTrue(isinstance(response.data, dict))
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["status_code"], 404)
        self.assertTrue(response.data["error"]) 