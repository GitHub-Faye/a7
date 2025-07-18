from rest_framework import serializers
from courses.models import Exercise

class StudentAnswerCorrectionSerializer(serializers.Serializer):
    """学生答案校正请求的序列化器"""
    exercise_id = serializers.IntegerField(
        required=True, 
        help_text="需要校正的练习题ID"
    )
    student_answer = serializers.CharField(
        required=True,
        help_text="学生提交的答案内容"
    )
    reference_answer = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="参考答案(对于选择题是选项字母，简答题是标准答案文本)"
    )
    session_id = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="会话ID，用于跟踪上下文"
    )
    
    def validate_exercise_id(self, value):
        """验证练习题ID是否存在"""
        try:
            Exercise.objects.get(id=value)
        except Exercise.DoesNotExist:
            raise serializers.ValidationError(f"ID为{value}的练习题不存在")
        return value 

class KnowledgePointProcessingSerializer(serializers.Serializer):
    """知识点处理请求的序列化器"""
    knowledge_points = serializers.JSONField(
        required=True,
        help_text="课程知识点数据，可以是知识点ID列表或完整的知识点数据"
    )
    title = serializers.CharField(
        required=True,
        help_text="生成内容的标题"
    )
    subject = serializers.CharField(
        required=True,
        help_text="学科"
    )
    grade_level = serializers.CharField(
        required=True,
        help_text="年级水平"
    )
    additional_requirements = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="额外要求或特定指导"
    )
    session_id = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="会话ID，用于跟踪多轮对话"
    )
    
    def validate_knowledge_points(self, value):
        """验证知识点数据"""
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("知识点数据必须是非空列表")
        return value 