import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from users.middleware.jwt_auth_middleware import JWTAuthMiddleware

User = get_user_model()

class JWTAuthMiddlewareTest(TestCase):
    """JWT认证中间件测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 为用户创建JWT令牌
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        # 请求工厂和响应模拟
        self.factory = RequestFactory()
        self.get_response_mock = MagicMock(return_value=JsonResponse({'message': 'success'}, status=200))
        self.middleware = JWTAuthMiddleware(self.get_response_mock)
        
        # 配置设置模拟
        self.settings_patcher = patch('users.middleware.jwt_auth_middleware.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.CUSTOM_JWT_ERROR_RESPONSE = True
    
    def tearDown(self):
        self.settings_patcher.stop()
    
    def test_exempt_url_not_authenticated(self):
        """测试豁免URL不会进行认证处理"""
        # 创建一个豁免URL的请求
        request = self.factory.get('/api/token/')
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证get_response被调用，没有进行认证处理
        self.get_response_mock.assert_called_once_with(request)
    
    @patch('users.middleware.jwt_auth_middleware.logger')
    def test_valid_token_authenticates_user(self, mock_logger):
        """测试有效令牌能正确认证用户"""
        # 创建带有有效令牌的请求
        request = self.factory.get('/api/users/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证认证成功日志被记录
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('认证成功', call_args)
        self.assertIn(self.user.username, call_args)
        
        # 验证令牌信息被保存到请求中
        self.assertTrue(hasattr(request, 'token'))
        self.assertTrue(hasattr(request, 'token_payload'))
        
        # 验证get_response被调用
        self.get_response_mock.assert_called_once_with(request)
    
    @patch('users.middleware.jwt_auth_middleware.logger')
    def test_invalid_token_returns_error(self, mock_logger):
        """测试无效令牌返回错误响应"""
        # 创建带有无效令牌的请求
        request = self.factory.get('/api/users/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalidtoken'
        request.path = '/api/users/'  # 为了测试API自定义响应
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证认证失败日志被记录
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        self.assertIn('认证失败', call_args)
        
        # 验证返回了401错误
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['error'])
        # 修改测试断言，匹配实际实现中的消息文本
        self.assertIn('无效的认证令牌', response_data['message'])
    
    @patch('users.middleware.jwt_auth_middleware.logger')
    def test_no_token_passes_to_next_middleware(self, mock_logger):
        """测试没有令牌的请求会传递给下一个中间件"""
        # 创建没有令牌的请求
        request = self.factory.get('/api/users/')
        
        # 执行中间件
        response = self.middleware(request)
        
        # 验证认证日志没有被记录
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()
        
        # 验证get_response被调用
        self.get_response_mock.assert_called_once_with(request)
    
    @patch('users.middleware.jwt_auth_middleware.logger')
    def test_expired_token_returns_error(self, mock_logger):
        """测试过期令牌返回错误响应"""
        # 模拟令牌验证失败的情况
        with patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate') as mock_authenticate:
            from rest_framework_simplejwt.exceptions import TokenError
            mock_authenticate.side_effect = TokenError('Token has expired')
            
            # 创建带有过期令牌的请求
            request = self.factory.get('/api/users/')
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
            request.path = '/api/users/'  # 为了测试API自定义响应
            
            # 执行中间件
            response = self.middleware(request)
            
            # 验证认证失败日志被记录
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            self.assertIn('认证失败', call_args)
            self.assertIn('Token error', call_args)
            
            # 验证返回了401错误
            self.assertEqual(response.status_code, 401)
            response_data = json.loads(response.content)
            self.assertTrue(response_data['error'])
            self.assertIn('令牌已过期', response_data['message']) 