from rest_framework import serializers
from .models import CourseProgress, LearningRecord, StudentAnswer, Exercise, KnowledgePoint

class KnowledgePointProgressSerializer(serializers.ModelSerializer):
    """知识点学习进度序列化器"""
    class Meta:
        model = KnowledgePoint
        fields = ['id', 'title', 'is_required', 'estimated_time']
        read_only_fields = ['id', 'title']


class ExerciseProgressSerializer(serializers.ModelSerializer):
    """练习题进度序列化器"""
    correctness_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'type', 'difficulty', 'is_required', 
                 'correct_count', 'attempt_count', 'correctness_rate']
        read_only_fields = ['id', 'title', 'type', 'difficulty', 
                           'correct_count', 'attempt_count', 'correctness_rate']


class StudentAnswerSerializer(serializers.ModelSerializer):
    """学生答案序列化器"""
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    
    class Meta:
        model = StudentAnswer
        fields = ['id', 'exercise', 'exercise_title', 'content', 'score', 
                 'is_correct', 'attempt_count', 'feedback', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']


class LearningRecordSerializer(serializers.ModelSerializer):
    """学习记录序列化器"""
    
    class Meta:
        model = LearningRecord
        fields = [
            'id', 'student', 'course', 'knowledge_point', 'status',
            'progress', 'time_spent', 'last_accessed', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'student', 'course', 'knowledge_point', 'created_at', 'updated_at']


class LearningRecordUpdateSerializer(serializers.ModelSerializer):
    """学习记录更新序列化器"""
    
    class Meta:
        model = LearningRecord
        fields = ['status', 'progress', 'time_spent']
        
    def validate_progress(self, value):
        """验证进度值在0-100之间"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("进度值必须在0到100之间")
        return value
        
    def validate_time_spent(self, value):
        """验证学习时间为正值"""
        if value < 0:
            raise serializers.ValidationError("学习时间必须为非负值")
        return value


class CourseProgressSerializer(serializers.ModelSerializer):
    """课程进度序列化器"""
    student_name = serializers.CharField(source='student.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseProgress
        fields = ['id', 'student', 'student_name', 'course', 'course_title', 
                 'overall_progress', 'required_completed', 'correctness_rate',
                 'total_time_spent', 'is_completed', 'completion_date', 'last_activity']
        read_only_fields = ['id', 'student', 'course', 'overall_progress', 'required_completed',
                           'correctness_rate', 'total_time_spent', 'is_completed', 
                           'completion_date', 'last_activity']


class CourseProgressDetailSerializer(serializers.ModelSerializer):
    """课程进度详情序列化器"""
    
    class Meta:
        model = CourseProgress
        fields = [
            'id', 'student', 'course', 'is_completed', 'completion_date',
            'overall_progress', 'required_completed', 'correctness_rate',
            'total_time_spent', 'last_activity'
        ]
        read_only_fields = ['id', 'student', 'course', 'is_completed', 'completion_date'] 