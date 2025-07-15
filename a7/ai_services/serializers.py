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