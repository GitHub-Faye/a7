from rest_framework import serializers
from .models import Course, KnowledgePoint, Courseware
from users.models import User

class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器，用于读取课程信息"""
    
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'subject', 'grade_level', 
                 'teacher', 'teacher_name', 'created_at']
        read_only_fields = ['teacher', 'created_at']
    
    def get_teacher_name(self, obj):
        """获取教师姓名"""
        if obj.teacher:
            return f"{obj.teacher.first_name} {obj.teacher.last_name}".strip() or obj.teacher.username
        return ""


class CourseCreateSerializer(serializers.ModelSerializer):
    """课程创建序列化器"""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'subject', 'grade_level']
    
    def create(self, validated_data):
        # 设置当前请求用户为教师
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class CourseUpdateSerializer(serializers.ModelSerializer):
    """课程更新序列化器"""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'subject', 'grade_level'] 