from rest_framework import serializers

class KnowledgePointToPPTSerializer(serializers.Serializer):
    """
    用于知识点到PPT转换请求的序列化器
    验证知识点转PPT所需的各项参数
    """
    # 必填字段：知识点ID列表
    knowledge_point_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        help_text="要转换为PPT的知识点ID列表，至少需要一个ID"
    )
    
    # 可选字段，均提供默认值
    include_children = serializers.BooleanField(
        default=True, 
        help_text="是否包含子知识点，默认为true"
    )
    
    max_depth = serializers.IntegerField(
        min_value=1, 
        max_value=5, 
        default=3,
        help_text="包含子知识点的最大深度，范围1-5，默认为3"
    )
    
    format = serializers.ChoiceField(
        choices=['pptx', 'pdf', 'html'],
        default='pptx',
        help_text="输出格式，可选值：pptx, pdf, html，默认为pptx"
    )
    
    theme = serializers.CharField(
        required=False, 
        default='hierarchy-default',
        help_text="演示文稿主题，默认为'hierarchy-default'，可选值：'hierarchy-default', 'hierarchy-teaching', 'hierarchy-minimalist', 'default'"
    )
    
    visual_style = serializers.ChoiceField(
        choices=['default', 'teaching', 'minimalist'],
        required=False,
        default='default',
        help_text="视觉样式，可选值：default(默认层级样式), teaching(教学型), minimalist(简约型)"
    )
    
    color_scheme = serializers.ChoiceField(
        choices=['blue', 'red', 'green', 'purple', 'dark', 'light'],
        required=False,
        default='blue',
        help_text="配色方案，可选值：blue(蓝色系), red(红色系), green(绿色系), purple(紫色系), dark(暗色), light(亮色)"
    )
    
    show_relations = serializers.BooleanField(
        default=True,
        required=False,
        help_text="是否显示知识点之间的关系指示器，默认为true"
    )
    
    title = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="自定义演示标题，可选"
    )
    
    include_course_info = serializers.BooleanField(
        default=True,
        help_text="是否包含课程信息，默认为true"
    )
    
    use_ai = serializers.BooleanField(
        default=False, 
        required=False,
        help_text="是否使用AI服务生成Markdown，默认为false"
    )
    
    return_file_content = serializers.BooleanField(
        default=False,
        required=False,
        help_text="是否直接返回文件内容（Base64编码），而不是URL，默认为false"
    )
    
    def validate_knowledge_point_ids(self, value):
        """
        验证知识点ID列表，检查ID是否有重复
        """
        # 检查ID列表是否有重复
        if len(value) != len(set(value)):
            raise serializers.ValidationError("知识点ID列表中包含重复ID")
        return value
    
    def validate(self, data):
        """
        对整体数据进行验证
        """
        # 如果不包含子知识点，但设置了max_depth > 1，添加警告
        if not data.get('include_children') and data.get('max_depth', 3) > 1:
            # 这里只是添加警告，不影响验证结果
            # 在真实环境中可以通过日志记录
            pass
            
        # 如果选择了visual_style，自动映射到对应的theme
        visual_style = data.get('visual_style')
        if visual_style and visual_style != 'default':
            data['theme'] = f'hierarchy-{visual_style}'
            
        return data 