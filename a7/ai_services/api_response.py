"""
API响应格式化工具模块

提供用于生成标准化API响应的辅助函数。
"""

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import exceptions
from typing import Any, Dict, Optional


def create_api_response(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
    message: Optional[str] = None,
    status_code: int = 200,
    errors: Any = None,
    **kwargs: Any
) -> Response:
    """
    创建一个标准化的API响应。
    
    Args:
        success: 响应是否成功
        data: 响应数据（成功时）
        error_code: 错误码（失败时）
        message: 响应消息
        status_code: HTTP状态码
        errors: 详细错误信息（失败时）
        **kwargs: 其他要包含在响应中的任意数据
        
    Returns:
        一个DRF的Response对象
    """
    response_body = {
        "success": success,
        "status_code": status_code,
    }
    
    if success:
        response_body["data"] = data
        if message:
            response_body["message"] = message
    else:
        response_body["error"] = {
            "code": error_code,
            "message": message,
        }
        # 添加详细错误信息
        if errors:
            response_body["error"]["details"] = errors
        # 直接添加error_code到顶层，以便与测试兼容
        response_body["error_code"] = error_code
    
    # 添加其他任意数据
    response_body.update(kwargs)
    
    return Response(response_body, status=status_code)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，确保所有API错误都使用统一的响应格式。
    
    Args:
        exc: 捕获的异常
        context: 异常上下文
        
    Returns:
        一个标准化的错误响应
    """
    # 首先调用DRF的默认异常处理器
    response = exception_handler(exc, context)
    
    # 如果没有处理，返回None让Django处理
    if response is None:
        return None
    
    # 获取错误详情
    error_details = None
    if hasattr(exc, 'detail'):
        error_details = exc.detail
    
    # 确定错误代码
    error_code = "API_ERROR"
    if isinstance(exc, exceptions.ValidationError):
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, exceptions.AuthenticationFailed):
        error_code = "AUTHENTICATION_FAILED"
    elif isinstance(exc, exceptions.NotAuthenticated):
        error_code = "NOT_AUTHENTICATED"
    elif isinstance(exc, exceptions.PermissionDenied):
        error_code = "PERMISSION_DENIED"
    elif isinstance(exc, exceptions.NotFound):
        error_code = "NOT_FOUND"
    elif isinstance(exc, exceptions.MethodNotAllowed):
        error_code = "METHOD_NOT_ALLOWED"
    elif isinstance(exc, exceptions.Throttled):
        error_code = "THROTTLED"
    
    # 获取错误消息
    error_message = str(exc)
    if not error_message and hasattr(exc, '__class__'):
        error_message = f"{exc.__class__.__name__}"
    
    # 创建统一的错误响应
    return create_api_response(
        success=False,
        error_code=error_code,
        message=error_message,
        errors=error_details,
        status_code=response.status_code
    ) 