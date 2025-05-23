import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

# 创建处理中间件日志记录器
logger = logging.getLogger('request_processor')

class RequestProcessorMiddleware:
    """
    请求内容处理中间件
    
    负责标准化请求内容和响应格式
    - JSON请求内容验证和转换
    - 为响应添加标准化头部
    - 为API返回标准化的响应格式
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 最大请求大小（默认10MB）
        self.max_request_size = getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024)
        # 是否标准化响应
        self.standardize_response = getattr(settings, 'STANDARDIZE_API_RESPONSE', False)
        # 额外响应头
        self.extra_headers = getattr(settings, 'API_EXTRA_HEADERS', {})
        # 排除路径
        self.excluded_paths = getattr(settings, 'PROCESSOR_EXCLUDE_PATHS', [
            '/admin/',
            '/static/',
            '/media/',
        ])
    
    def __call__(self, request):
        # 检查是否排除处理
        if self._should_process_url(request.path):
            # 前处理：检查请求
            processed_request = self._process_request(request)
            if isinstance(processed_request, JsonResponse):
                # 如果前处理返回了响应，直接返回
                return processed_request
            
            # 执行视图
            response = self.get_response(request)
            
            # 后处理：处理响应
            processed_response = self._process_response(request, response)
            return processed_response
        else:
            # 如果路径被排除，不进行处理
            return self.get_response(request)
    
    def _should_process_url(self, url):
        """检查URL是否应该被处理"""
        return not any(url.startswith(path) for path in self.excluded_paths)
    
    def _process_request(self, request):
        """处理请求内容"""
        # 内容长度检查
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"请求大小超过限制: {content_length} > {self.max_request_size}")
            return JsonResponse({
                'error': True,
                'message': '请求内容过大',
                'detail': f'最大允许大小: {self.max_request_size/1024/1024}MB'
            }, status=413)
        
        # 如果是JSON内容类型，尝试解析JSON
        if request.content_type == 'application/json' and request.body:
            try:
                json_data = json.loads(request.body.decode('utf-8'))
                # 将解析后的JSON数据保存到request属性中，方便后续使用
                request.json_data = json_data
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析错误: {str(e)}")
                return JsonResponse({
                    'error': True,
                    'message': 'JSON格式错误',
                    'detail': str(e)
                }, status=400)
            except UnicodeDecodeError as e:
                logger.warning(f"编码错误: {str(e)}")
                return JsonResponse({
                    'error': True,
                    'message': '请求编码错误',
                    'detail': str(e)
                }, status=400)
        
        return request
    
    def _process_response(self, request, response):
        """处理响应内容"""
        # 添加额外响应头
        for header_name, header_value in self.extra_headers.items():
            response[header_name] = header_value
        
        # 添加安全相关的响应头
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 如果启用了标准化API响应
        if self.standardize_response and request.path.startswith('/api/'):
            # 只对JSON响应进行标准化
            if hasattr(response, 'accepted_media_type') and 'application/json' in response.accepted_media_type:
                # 检查响应的状态码
                if 200 <= response.status_code < 300:
                    # 成功响应
                    self._standardize_success_response(response)
                elif response.status_code >= 400:
                    # 错误响应
                    self._standardize_error_response(response)
        
        return response
    
    def _standardize_success_response(self, response):
        """标准化成功响应"""
        if hasattr(response, 'data'):
            # 获取原始数据
            original_data = response.data
            
            # 检查是否已经是标准格式
            if isinstance(original_data, dict) and 'data' in original_data and ('status' in original_data or 'success' in original_data):
                # 已经是标准格式，不需要再处理
                return
            
            # 标准化响应格式
            standardized_data = {
                'success': True,
                'status_code': response.status_code,
                'data': original_data
            }
            
            # 更新响应数据
            response.data = standardized_data
            response._is_rendered = False
            response.render()
    
    def _standardize_error_response(self, response):
        """标准化错误响应"""
        if hasattr(response, 'data'):
            # 获取原始数据
            original_data = response.data
            
            # 检查是否已经是标准格式
            if isinstance(original_data, dict) and 'error' in original_data and ('message' in original_data or 'detail' in original_data):
                # 已经是标准格式，不需要再处理
                return
            
            # 准备错误消息
            if isinstance(original_data, dict) and 'detail' in original_data:
                error_message = original_data['detail']
            elif isinstance(original_data, str):
                error_message = original_data
            else:
                error_message = '请求处理出错'
            
            # 标准化响应格式
            standardized_data = {
                'error': True,
                'status_code': response.status_code,
                'message': error_message,
            }
            
            # 如果原始数据是字典且包含额外信息，保留这些信息
            if isinstance(original_data, dict):
                for key, value in original_data.items():
                    if key not in ['error', 'status_code', 'message', 'detail']:
                        standardized_data[key] = value
            
            # 更新响应数据
            response.data = standardized_data
            response._is_rendered = False
            response.render() 