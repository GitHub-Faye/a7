from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from ai_services.api_response import create_api_response
import os
import uuid

def validate_required_params(request, param_names, error_status=400):
    """验证请求参数是否存在"""
    missing_params = []
    
    # 处理GET参数
    if request.method == 'GET':
        for param in param_names:
            if param not in request.GET and param not in request.query_params:
                missing_params.append(param)
    
    # 处理POST/PUT/PATCH参数
    else:
        # 尝试从JSON请求体中获取
        if hasattr(request, 'json_data') and isinstance(request.json_data, dict):
            for param in param_names:
                if param not in request.json_data:
                    missing_params.append(param)
        # 尝试从data属性获取 (REST framework)
        elif hasattr(request, 'data') and isinstance(request.data, dict):
            for param in param_names:
                if param not in request.data:
                    missing_params.append(param)
        # 尝试从表单数据中获取
        else:
            for param in param_names:
                if param not in request.POST:
                    missing_params.append(param)
    
    if missing_params:
        return create_api_response(
            success=False,
            error_code="MISSING_PARAMETERS",
            message=str(_('缺少必要的参数')),  # 转换为字符串
            errors={'missing_params': missing_params},
            status_code=error_status
        )
    
    return None  # 验证通过，返回None 

def courseware_file_path(instance, filename):
    """
    为上传的课件文件生成存储路径
    格式: coursewares/<课程ID>/<文件类型>/<文件名>
    """
    # 获取课程ID
    course_id = instance.courseware.course.id
    # 获取简化的文件类型
    file_type = get_simple_file_type(instance.file_type) if hasattr(instance, 'file_type') and instance.file_type else 'others'
    # 返回完整路径
    return f"coursewares/{course_id}/{file_type}/{filename}"

def get_simple_file_type(mime_type):
    """
    从MIME类型获取简化的文件类型分类
    """
    if mime_type.startswith('image/'):
        return 'images'
    elif mime_type.startswith('video/'):
        return 'videos'
    elif mime_type.startswith('audio/'):
        return 'audios'
    elif mime_type in ['application/pdf']:
        return 'pdfs'
    elif mime_type in ['application/msword', 
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return 'documents'
    elif mime_type in ['application/vnd.ms-powerpoint',
                      'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
        return 'presentations'
    else:
        return 'others'

def validate_file_type(file_obj, allowed_types=None):
    """
    验证文件类型是否在允许的类型列表中
    """
    if allowed_types is None:
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ]
    
    # 获取文件类型
    content_type = getattr(file_obj, 'content_type', None)
    if content_type and content_type in allowed_types:
        return True
    
    # 如果没有content_type或不在允许列表中，检查扩展名
    filename = file_obj.name
    ext = os.path.splitext(filename)[1].lower()[1:]  # 去掉点号
    ext_map = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }
    
    return ext in ext_map and ext_map[ext] in allowed_types

def validate_file_size(file_obj, max_size_mb=10):
    """
    验证文件大小是否超过最大限制
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_obj.size <= max_size_bytes 