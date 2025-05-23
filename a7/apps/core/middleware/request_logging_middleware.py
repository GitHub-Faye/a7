import logging
import time
import json
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

# 创建请求日志记录器
logger = logging.getLogger('request_log')

class RequestLoggingMiddleware:
    """
    请求日志中间件
    
    记录请求的详细信息，包括URL、方法、头部、内容等
    记录响应时间和状态码等性能指标
    可用于性能监控和问题排查
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 日志级别：可在settings中配置，默认为INFO
        self.log_level = getattr(settings, 'REQUEST_LOG_LEVEL', 'INFO')
        # 是否记录请求体：可在settings中配置，默认为False（避免记录敏感信息）
        self.log_request_body = getattr(settings, 'LOG_REQUEST_BODY', False)
        # 最大记录长度：防止过大的请求/响应导致日志过大
        self.max_body_length = getattr(settings, 'MAX_BODY_LOG_LENGTH', 1000)
        # 要排除的路径：不记录日志的URL路径
        self.excluded_paths = getattr(settings, 'REQUEST_LOG_EXCLUDE_PATHS', [
            '/admin/jsi18n/',
            '/static/',
            '/media/',
            '/health-check/',
        ])
        
    def __call__(self, request):
        # 检查路径是否被排除
        if self._should_log_url(request.path):
            # 记录请求开始
            start_time = time.time()
            request_time = timezone.now()
            
            # 获取请求信息
            request_data = self._get_request_data(request)
            
            # 执行请求
            response = self.get_response(request)
            
            # 计算处理时间
            duration = time.time() - start_time
            
            # 记录响应信息
            response_data = self._get_response_data(response, duration)
            
            # 记录日志
            self._log_request(request, request_data, response_data, request_time, duration)
            
            return response
        else:
            # 如果路径被排除，不记录日志
            return self.get_response(request)
    
    def _should_log_url(self, url):
        """检查URL是否应该被记录"""
        return not any(url.startswith(path) for path in self.excluded_paths)
    
    def _get_request_data(self, request):
        """获取请求信息"""
        data = {
            'method': request.method,
            'path': request.path,
            'query_params': request.GET.dict(),
            'headers': self._get_safe_headers(request),
            'client_ip': self._get_client_ip(request),
        }
        
        # 如果配置了记录请求体且请求体不为空
        if self.log_request_body and request.body:
            try:
                # 尝试解析JSON请求体
                body = json.loads(request.body.decode('utf-8'))
                # 敏感字段处理（如密码）
                if 'password' in body:
                    body['password'] = '******'
                if 'token' in body:
                    body['token'] = '******'
                
                # 限制长度
                body_str = json.dumps(body)
                if len(body_str) > self.max_body_length:
                    body_str = body_str[:self.max_body_length] + '... [截断]'
                
                data['body'] = body_str
            except (ValueError, UnicodeDecodeError):
                # 非JSON请求体，记录长度信息
                data['body'] = f'[非JSON内容，长度: {len(request.body)}字节]'
        
        # 添加用户信息（如果已认证）
        if hasattr(request, 'user') and request.user.is_authenticated:
            data['user'] = request.user.username
            if hasattr(request.user, 'role'):
                data['role'] = request.user.role
        
        return data
    
    def _get_response_data(self, response, duration):
        """获取响应信息"""
        data = {
            'status_code': response.status_code,
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
            'duration': f'{duration:.4f}秒',
        }
        
        # 记录响应内容类型
        if hasattr(response, 'headers') and 'Content-Type' in response.headers:
            data['content_type'] = response.headers['Content-Type']
        
        return data
    
    def _log_request(self, request, request_data, response_data, request_time, duration):
        """记录请求和响应信息"""
        # 成功响应（2xx）详细级别记录为INFO，其他为WARNING
        log_func = logger.info if 200 <= response_data['status_code'] < 300 else logger.warning
        
        # 构建日志消息
        message = (
            f"[{request_data['method']}] {request_data['path']} - {response_data['status_code']} "
            f"({response_data['duration']})"
        )
        
        # 构建详细日志数据
        log_data = {
            'timestamp': request_time.isoformat(),
            'request': request_data,
            'response': response_data,
        }
        
        # 根据配置的级别记录日志
        if self.log_level == 'DEBUG':
            logger.debug(message, extra={'data': log_data})
        elif self.log_level == 'INFO':
            log_func(message, extra={'data': log_data})
        elif self.log_level == 'WARNING' and response_data['status_code'] >= 400:
            logger.warning(message, extra={'data': log_data})
        elif self.log_level == 'ERROR' and response_data['status_code'] >= 500:
            logger.error(message, extra={'data': log_data})
    
    def _get_safe_headers(self, request):
        """获取安全的请求头信息（排除敏感信息）"""
        headers = {}
        for key, value in request.META.items():
            # 只记录HTTP_开头的头部
            if key.startswith('HTTP_'):
                name = key[5:].lower().replace('_', '-')
                # 敏感头部处理
                if name in ['authorization', 'cookie', 'proxy-authorization']:
                    value = '******'
                headers[name] = value
        return headers
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown') 