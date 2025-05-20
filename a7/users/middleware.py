import json
import logging
from django.http import JsonResponse
from django.urls import resolve
from django.conf import settings

# 创建权限日志记录器
logger = logging.getLogger('permission_log')


class RoleBasedPermissionMiddleware:
    """
    基于角色的权限检查中间件
    记录权限检查结果并提供自定义的权限拒绝响应
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 在视图处理前的逻辑
        
        # 检查请求路径，排除不需要检查的路径（如静态文件、管理页面等）
        path = request.path_info.lstrip('/')
        if any(path.startswith(url) for url in self.get_exempt_urls()):
            return self.get_response(request)
        
        # 如果用户未登录，直接执行后续过程
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # 获取当前请求的视图函数
        try:
            resolved = resolve(request.path)
            view_name = resolved.view_name
        except:
            view_name = 'unknown'
        
        # 记录访问尝试
        self.log_access_attempt(request, view_name)
        
        # 执行视图
        response = self.get_response(request)
        
        # 检查响应代码，记录权限拒绝情况
        if response.status_code in [401, 403]:
            self.log_permission_denied(request, view_name, response.status_code)
            
            # 如果设置了自定义的权限拒绝响应且是API请求
            if getattr(settings, 'CUSTOM_PERMISSION_DENIED_RESPONSE', False) and request.path.startswith('/api/'):
                return self.custom_permission_denied_response(request, response)
        
        return response
    
    def get_exempt_urls(self):
        """获取豁免URL，这些URL不需要进行权限检查"""
        return [
            'admin/',
            'static/',
            'media/',
            'api-auth/',
            'api/token/',
            'api/login/',
            'swagger/',
            'redoc/',
        ]
    
    def log_access_attempt(self, request, view_name):
        """记录访问尝试"""
        logger.info(
            f"访问尝试: 用户={request.user.username}, "
            f"角色={request.user.role}, "
            f"方法={request.method}, "
            f"路径={request.path}, "
            f"视图={view_name}"
        )
    
    def log_permission_denied(self, request, view_name, status_code):
        """记录权限拒绝情况"""
        logger.warning(
            f"权限拒绝: 用户={request.user.username}, "
            f"角色={request.user.role}, "
            f"方法={request.method}, "
            f"路径={request.path}, "
            f"视图={view_name}, "
            f"状态码={status_code}"
        )
    
    def custom_permission_denied_response(self, request, original_response):
        """提供自定义的权限拒绝响应"""
        if original_response.status_code == 401:
            message = "身份验证失败，请登录或提供有效的认证信息。"
        else:  # 403
            message = "您没有执行此操作的权限。"
            
            # 如果是API请求且原始响应有详细信息，尝试提取
            if hasattr(original_response, 'data') and 'detail' in original_response.data:
                message = original_response.data['detail']
        
        return JsonResponse({
            'error': True,
            'status_code': original_response.status_code,
            'message': message,
            'user_role': request.user.role if request.user.is_authenticated else None
        }, status=original_response.status_code) 