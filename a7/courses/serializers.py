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

# KnowledgePoint序列化器类
class KnowledgePointSerializer(serializers.ModelSerializer):
    """知识点序列化器，用于读取知识点信息"""
    
    course_title = serializers.SerializerMethodField()
    parent_title = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgePoint
        fields = ['id', 'title', 'content', 'importance', 'course', 'course_title', 
                 'parent', 'parent_title', 'children']
        read_only_fields = ['course', 'parent', 'children']
    
    def get_course_title(self, obj):
        """获取课程标题"""
        if obj.course:
            return obj.course.title
        return ""
    
    def get_parent_title(self, obj):
        """获取父知识点标题"""
        if obj.parent:
            return obj.parent.title
        return ""
    
    def get_children(self, obj):
        """获取子知识点列表（ID和标题）"""
        children = obj.children.all()
        if not children:
            return []
        return [{'id': child.id, 'title': child.title} for child in children]


class KnowledgePointCreateSerializer(serializers.ModelSerializer):
    """知识点创建序列化器"""
    
    class Meta:
        model = KnowledgePoint
        fields = ['title', 'content', 'importance', 'course', 'parent']
    
    def validate(self, data):
        """验证创建数据"""
        # 确保parent知识点属于同一个课程
        parent = data.get('parent')
        course = data.get('course')
        
        if parent and course and parent.course != course:
            raise serializers.ValidationError(
                {"parent": "父知识点必须属于同一个课程"}
            )
        
        return data


class KnowledgePointUpdateSerializer(serializers.ModelSerializer):
    """知识点更新序列化器"""
    
    class Meta:
        model = KnowledgePoint
        fields = ['title', 'content', 'importance', 'parent']
    
    def validate(self, data):
        """验证更新数据"""
        # 获取要更新的实例
        instance = self.instance
        
        # 确保parent知识点属于同一个课程
        parent = data.get('parent')
        if parent and instance.course != parent.course:
            raise serializers.ValidationError(
                {"parent": "父知识点必须属于同一个课程"}
            )
        
        # 检查是否会形成循环引用
        if parent and self._would_create_cycle(instance, parent):
            raise serializers.ValidationError(
                {"parent": "不能将知识点设为自己的子孙节点的父节点，这会形成循环引用"}
            )
            
        return data
    
    def _would_create_cycle(self, instance, new_parent):
        """检查是否会形成循环引用"""
        # 如果new_parent是该知识点本身，则形成直接循环
        if new_parent == instance:
            return True
            
        # 递归检查new_parent的所有祖先，看是否包含instance
        current = new_parent.parent
        while current:
            if current == instance:
                return True
            current = current.parent
            
        return False 

# Courseware序列化器
class CoursewareSerializer(serializers.ModelSerializer):
    """课件序列化器，用于读取课件信息"""
    
    course_title = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Courseware
        fields = ['id', 'title', 'content', 'type', 'type_display', 'course', 
                 'course_title', 'created_by', 'creator_name', 'created_at']
        read_only_fields = ['created_by', 'created_at']
    
    def get_course_title(self, obj):
        """获取课程标题"""
        if obj.course:
            return obj.course.title
        return ""
    
    def get_creator_name(self, obj):
        """获取创建者姓名"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return ""
    
    def get_type_display(self, obj):
        """获取课件类型显示名称"""
        return obj.get_type_display()


class CoursewareCreateSerializer(serializers.ModelSerializer):
    """课件创建序列化器"""
    
    class Meta:
        model = Courseware
        fields = ['title', 'content', 'type', 'course']
    
    def create(self, validated_data):
        # 设置当前请求用户为创建者
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CoursewareUpdateSerializer(serializers.ModelSerializer):
    """课件更新序列化器"""
    
    class Meta:
        model = Courseware
        fields = ['title', 'content', 'type'] 