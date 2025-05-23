import json
import unittest
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.utils import timezone

from apps.core.middleware.request_logging_middleware import RequestLoggingMiddleware
from apps.core.middleware.request_processor_middleware import RequestProcessorMiddleware

class RequestLoggingMiddlewareTest(TestCase):
    """请求日志中间件测试"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response_mock = MagicMock(return_value=JsonResponse({'message': 'success'}, status=200))
        self.middleware = RequestLoggingMiddleware(self.get_response_mock)
    
    @patch('apps.core.middleware.request_logging_middleware.logger')
    def test_excluded_path_not_logged(self, mock_logger):
        """测试排除的路径不会被记录"""
        # 创建一个排除路径的请求
        request = self.factory.get('/static/style.css')
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证日志记录器没有被调用
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()
        
        # 验证get_response被调用
        self.get_response_mock.assert_called_once_with(request)
    
    @patch('apps.core.middleware.request_logging_middleware.logger')
    def test_api_request_logged(self, mock_logger):
        """测试API请求被正确记录"""
        # 创建一个API请求
        request = self.factory.get('/api/users/')
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证日志记录器被调用
        mock_logger.info.assert_called_once()
        
        # 验证get_response被调用
        self.get_response_mock.assert_called_once_with(request)
    
    @patch('apps.core.middleware.request_logging_middleware.logger')
    def test_error_response_logged_as_warning(self, mock_logger):
        """测试错误响应被记录为警告"""
        # 创建一个会返回错误的响应的mock
        error_response_mock = MagicMock(return_value=JsonResponse({'error': 'Not found'}, status=404))
        middleware = RequestLoggingMiddleware(error_response_mock)
        
        # 创建请求
        request = self.factory.get('/api/users/999/')
        
        # 执行中间件
        response = middleware(request)
        
        # 验证日志记录器的warning被调用
        mock_logger.warning.assert_called_once()

class RequestProcessorMiddlewareTest(TestCase):
    """请求处理中间件测试"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response_mock = MagicMock(return_value=JsonResponse({'data': 'success'}, status=200))
        self.middleware = RequestProcessorMiddleware(self.get_response_mock)
    
    def test_excluded_path_not_processed(self):
        """测试排除的路径不会被处理"""
        # 创建一个排除路径的请求
        request = self.factory.get('/admin/login/')
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证get_response被调用，没有进行任何处理
        self.get_response_mock.assert_called_once_with(request)
    
    def test_invalid_json_request_returns_400(self):
        """测试无效的JSON请求返回400错误"""
        # 创建带有无效JSON的请求
        request = self.factory.post(
            '/api/users/',
            data='{invalid json}',
            content_type='application/json'
        )
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证返回了400错误
        self.assertEqual(response.status_code, 400)
        self.assertTrue(json.loads(response.content)['error'])
    
    def test_large_request_body_returns_413(self):
        """测试超大的请求体返回413错误"""
        # 暂时将最大请求大小设置为较小的值
        original_max_size = self.middleware.max_request_size
        self.middleware.max_request_size = 10
        
        # 创建一个大于最大请求大小的请求
        request = self.factory.post(
            '/api/users/',
            data='{"data": "x" * 100}',
            content_type='application/json'
        )
        # 手动设置内容长度
        request.META['CONTENT_LENGTH'] = 100
        
        # 执行中间件
        response = self.middleware(request)
        
        # 恢复原始最大请求大小
        self.middleware.max_request_size = original_max_size
        
        # 验证返回了413错误
        self.assertEqual(response.status_code, 413)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['error'])
        self.assertIn('请求内容过大', response_data['message'])
    
    def test_adds_security_headers(self):
        """测试添加安全相关的响应头"""
        # 创建请求
        request = self.factory.get('/api/users/')
        
        # 模拟返回的响应对象
        mock_response = JsonResponse({'data': 'test'})
        self.get_response_mock.return_value = mock_response
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证添加了安全响应头
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('Referrer-Policy', response)
    
    @unittest.skip("跳过此测试，因为需要DRF Response对象的特定实现")
    def test_response_standardization(self):
        """测试响应标准化 - 需要DRF Response对象，常规测试中难以模拟"""
        pass 