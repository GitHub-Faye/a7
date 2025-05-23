import logging
import time
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    InvalidToken, TokenError, AuthenticationFailed
)
from django.conf import settings

# 创建JWT认证日志记录器
logger = logging.getLogger('jwt_auth')

class JWTAuthMiddleware:
    """
    JWT令牌认证中间件
    
    检查请求头中的JWT令牌，验证其有效性
    - 处理令牌验证过程
    - 记录认证尝试和结果
    - 处理令牌失效或过期的情况
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth = JWTAuthentication()
        
    def __call__(self, request):
        # 开始计时，用于性能日志
        start_time = time.time()
        
        # 检查请求路径，排除不需要认证的路径
        path = request.path_info.lstrip('/')
        if any(path.startswith(url) for url in self.get_exempt_urls()):
            return self.get_response(request)
        
        # 检查请求头中是否有Authorization头
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header and auth_header.startswith('Bearer '):
            # 尝试验证令牌
            try:
                # 使用JWTAuthentication进行认证
                authenticated = self.auth.authenticate(request)
                
                if authenticated:
                    user, token = authenticated
                    # 在请求中保存令牌信息，供后续中间件使用
                    request.token = token
                    request.token_payload = token.payload
                    
                    # 记录成功认证
                    self.log_auth_success(request, user, time.time() - start_time)
                else:
                    # 记录认证失败
                    self.log_auth_failure(request, "No credentials were provided", time.time() - start_time)
            
            except InvalidToken as e:
                # 令牌无效
                self.log_auth_failure(request, f"Invalid token: {str(e)}", time.time() - start_time)
                
                # 如果配置为自定义响应且是API请求
                if getattr(settings, 'CUSTOM_JWT_ERROR_RESPONSE', False) and request.path.startswith('/api/'):
                    return self.custom_jwt_error_response(request, "无效的认证令牌，请重新登录")
                
            except TokenError as e:
                # 令牌错误（可能是过期）
                self.log_auth_failure(request, f"Token error: {str(e)}", time.time() - start_time)
                
                # 如果配置为自定义响应且是API请求
                if getattr(settings, 'CUSTOM_JWT_ERROR_RESPONSE', False) and request.path.startswith('/api/'):
                    return self.custom_jwt_error_response(request, "认证令牌已过期，请重新登录")
                
            except AuthenticationFailed as e:
                # 认证失败（如用户已禁用）
                self.log_auth_failure(request, f"Authentication failed: {str(e)}", time.time() - start_time)
                
                # 如果配置为自定义响应且是API请求
                if getattr(settings, 'CUSTOM_JWT_ERROR_RESPONSE', False) and request.path.startswith('/api/'):
                    return self.custom_jwt_error_response(request, "认证失败，用户可能已被禁用")
                
            except Exception as e:
                # 其他异常
                self.log_auth_failure(request, f"Unexpected error: {str(e)}", time.time() - start_time)
                
                # 如果配置为自定义响应且是API请求
                if getattr(settings, 'CUSTOM_JWT_ERROR_RESPONSE', False) and request.path.startswith('/api/'):
                    return self.custom_jwt_error_response(request, "认证处理过程中发生错误")
        
        # 执行下一个中间件/视图
        response = self.get_response(request)
        return response
    
    def get_exempt_urls(self):
        """获取豁免URL，这些URL不需要进行JWT认证"""
        return [
            'admin/',
            'static/',
            'media/',
            'api-auth/',
            'api/token/',
            'api/login/',
            'swagger/',
            'redoc/',
            'health-check/',
        ]
    
    def log_auth_success(self, request, user, elapsed_time):
        """记录认证成功"""
        logger.info(
            f"认证成功: 用户={user.username}, "
            f"角色={user.role if hasattr(user, 'role') else 'N/A'}, "
            f"方法={request.method}, "
            f"路径={request.path}, "
            f"IP={self.get_client_ip(request)}, "
            f"处理时间={elapsed_time:.4f}秒"
        )
    
    def log_auth_failure(self, request, reason, elapsed_time):
        """记录认证失败"""
        logger.warning(
            f"认证失败: "
            f"原因={reason}, "
            f"方法={request.method}, "
            f"路径={request.path}, "
            f"IP={self.get_client_ip(request)}, "
            f"处理时间={elapsed_time:.4f}秒"
        )
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def custom_jwt_error_response(self, request, message):
        """提供自定义的JWT错误响应"""
        return JsonResponse({
            'error': True,
            'status_code': 401,
            'message': message,
            'detail': _('认证令牌无效或已过期')
        }, status=401) 