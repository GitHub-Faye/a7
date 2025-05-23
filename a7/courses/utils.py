from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

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
        return JsonResponse({
            'success': False,
            'message': _('缺少必要的参数'),
            'errors': [_('缺少参数: {}').format(', '.join(missing_params))]
        }, status=error_status)
    
    return None  # 验证通过，返回None 