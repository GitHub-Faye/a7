from rest_framework import serializers
from .utils import OutputFormat, DEFAULT_THEMES


class MarpConversionSerializer(serializers.Serializer):
    """
    用于Markdown到演示格式转换的序列化器
    """
    content = serializers.CharField(
        required=True,
        help_text="要转换的Markdown内容，支持Marp语法"
    )
    format = serializers.CharField(
        required=True,
        help_text=f"输出格式，支持: {', '.join([f.value for f in OutputFormat])}"
    )
    theme = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text=f"可选的Marp主题，推荐值: {', '.join(DEFAULT_THEMES)}，也支持自定义主题"
    )
    
    def validate_format(self, value):
        """验证格式是否支持"""
        try:
            # 尝试转换为枚举值，如果失败则引发ValueError
            OutputFormat(value.lower())
            return value.lower()
        except ValueError:
            supported_formats = ", ".join([f.value for f in OutputFormat])
            raise serializers.ValidationError(f"不支持的输出格式: {value}。支持的格式有: {supported_formats}")
    
    def validate_theme(self, value):
        """验证主题"""
        if value and value.lower() not in [theme.lower() for theme in DEFAULT_THEMES]:
            # 主题不在默认列表中，但我们不抛出错误，因为用户可能使用自定义主题
            # 可以考虑添加警告日志
            pass
        return value 