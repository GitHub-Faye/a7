import os
import tempfile
from unittest import mock
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from marp_service.exceptions import MarpServiceError
from marp_service.utils import OutputFormat


class MarpConversionViewTests(TestCase):
    """测试MarpConversionView视图功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('marp_service:convert')
        self.valid_data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'pdf',
            'theme': 'default'
        }
    
    def test_post_invalid_data(self):
        """测试提交无效数据时返回400错误"""
        # 缺少content字段
        data = {'format': 'pdf'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 无效的格式
        data = {'content': '# Test', 'format': 'invalid'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @mock.patch('marp_service.views.convert_markdown_to_format')
    def test_post_successful_conversion(self, mock_convert):
        """测试成功转换Markdown的情况"""
        # 创建临时文件模拟转换结果
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(b'PDF content')
        temp_file.close()
        
        # 配置mock返回临时文件路径
        mock_convert.return_value = temp_file.name
        
        try:
            # 发送请求
            response = self.client.post(self.url, self.valid_data, format='json')
            
            # 验证响应状态码
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # 验证文件响应头
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertEqual(response['Content-Disposition'], 'attachment; filename="presentation.pdf"')
            
            # 验证服务函数被正确调用
            mock_convert.assert_called_once_with(
                content=self.valid_data['content'],
                output_format=self.valid_data['format'],
                theme=self.valid_data['theme']
            )
            
            # 临时删除前关闭文件句柄
            response.close()
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except PermissionError:
                # 如果文件被占用，可以选择忽略或记录日志
                pass
    
    @mock.patch('marp_service.views.convert_markdown_to_format')
    def test_post_value_error(self, mock_convert):
        """测试转换过程中发生ValueError的情况"""
        # 配置mock抛出ValueError
        mock_convert.side_effect = ValueError("不支持的格式")
        
        # 发送请求
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        # 匹配实际响应格式
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['status_code'], 415)
        self.assertIn('error', response.data)
    
    @mock.patch('marp_service.views.convert_markdown_to_format')
    def test_post_marp_service_error(self, mock_convert):
        """测试转换过程中发生MarpServiceError的情况"""
        # 配置mock抛出MarpServiceError
        mock_convert.side_effect = MarpServiceError("转换失败")
        
        # 发送请求
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 匹配实际响应格式
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['status_code'], 500)
        self.assertIn('error', response.data)
    
    @mock.patch('marp_service.views.convert_markdown_to_format')
    def test_post_unexpected_error(self, mock_convert):
        """测试转换过程中发生未预期异常的情况"""
        # 配置mock抛出未预期异常
        mock_convert.side_effect = Exception("未知错误")
        
        # 发送请求
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 匹配实际响应格式
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['status_code'], 500)
        self.assertIn('error', response.data) 