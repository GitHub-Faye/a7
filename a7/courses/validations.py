from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status

def validate_text_field(request, required_fields):
    """
    验证请求中是否包含所有必需的文本字段
    
    参数:
    - request: HTTP请求对象
    - required_fields: 必需字段名称列表
    
    返回:
    - 如果验证失败，返回Response对象
    - 如果验证成功，返回None
    """
    missing_fields = []
    
    # 检查query_params或data中是否包含所有必需字段
    for field in required_fields:
        # 先检查query_params（GET请求）
        if hasattr(request, 'query_params') and field in request.query_params:
            value = request.query_params.get(field)
            if value and value.strip():
                continue
        
        # 再检查data（POST请求）
        if hasattr(request, 'data') and field in request.data:
            value = request.data.get(field)
            if value and (not isinstance(value, str) or value.strip()):
                continue
        
        # 字段缺失或为空
        missing_fields.append(field)
    
    # 如果有缺失字段，返回错误响应
    if missing_fields:
        return Response({
            "success": False,
            "message": "缺少必需参数",
            "errors": [f"参数 '{field}' 是必需的" for field in missing_fields]
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证通过
    return None

class ValidationUtils:
    """通用验证工具类"""
    
    @staticmethod
    def validate_text_field(value, field_name, min_length=1, max_length=None):
        """验证文本字段"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                {field_name: _("此字段不能为空")}
            )
        
        if min_length and len(value.strip()) < min_length:
            raise serializers.ValidationError(
                {field_name: _(f"此字段长度不能小于{min_length}个字符")}
            )
            
        if max_length and len(value.strip()) > max_length:
            raise serializers.ValidationError(
                {field_name: _(f"此字段长度不能超过{max_length}个字符")}
            )
        
        return value.strip()

    @staticmethod
    def validate_existence(model, id_value, field_name="id"):
        """验证对象是否存在"""
        if not id_value:
            return None
            
        try:
            obj = model.objects.get(id=id_value)
            return obj
        except model.DoesNotExist:
            raise serializers.ValidationError(
                {field_name: _(f"ID为{id_value}的对象不存在")}
            )
            
    @staticmethod
    def validate_uniqueness(model, field_name, value, exclude_id=None, error_message=None):
        """验证字段值的唯一性"""
        if not value:
            return value
            
        query = {field_name: value}
        if exclude_id:
            qs = model.objects.filter(**query).exclude(id=exclude_id)
        else:
            qs = model.objects.filter(**query)
            
        if qs.exists():
            raise serializers.ValidationError(
                {field_name: error_message or _(f"此{field_name}已存在")}
            )
            
        return value 