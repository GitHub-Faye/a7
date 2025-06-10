"""
API响应格式化工具模块

提供用于生成标准化API响应的辅助函数。
"""

from rest_framework.response import Response
from typing import Any, Dict, Optional


def create_api_response(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
    message: Optional[str] = None,
    status_code: int = 200,
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
    
    # 添加其他任意数据
    response_body.update(kwargs)
    
    return Response(response_body, status=status_code) 