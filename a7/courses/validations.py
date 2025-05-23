from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

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