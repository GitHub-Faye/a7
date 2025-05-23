from rest_framework import serializers
from .models import Course, KnowledgePoint, Courseware
from users.models import User
from .validations import ValidationUtils
from django.utils.translation import gettext_lazy as _

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
    
    def validate_title(self, value):
        """验证课程标题"""
        return ValidationUtils.validate_text_field(
            value, "title", min_length=3, max_length=100
        )
    
    def validate_subject(self, value):
        """验证学科名称"""
        return ValidationUtils.validate_text_field(
            value, "subject", min_length=1, max_length=50
        )
    
    def validate_grade_level(self, value):
        """验证年级水平"""
        return ValidationUtils.validate_text_field(
            value, "grade_level", min_length=1, max_length=20
        )
        
    def validate(self, data):
        """验证整体数据"""
        # 验证标题的唯一性
        title = data.get('title')
        if title:
            ValidationUtils.validate_uniqueness(
                Course, 'title', title, 
                error_message=_("同名课程已存在，请使用不同的标题")
            )
        return data
    
    def create(self, validated_data):
        # 设置当前请求用户为教师
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class CourseUpdateSerializer(serializers.ModelSerializer):
    """课程更新序列化器"""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'subject', 'grade_level']
        
    def validate_title(self, value):
        """验证课程标题"""
        return ValidationUtils.validate_text_field(
            value, "title", min_length=3, max_length=100
        )
    
    def validate_subject(self, value):
        """验证学科名称"""
        return ValidationUtils.validate_text_field(
            value, "subject", min_length=1, max_length=50
        )
    
    def validate_grade_level(self, value):
        """验证年级水平"""
        return ValidationUtils.validate_text_field(
            value, "grade_level", min_length=1, max_length=20
        )
        
    def validate(self, data):
        """验证整体数据"""
        # 验证标题的唯一性（排除自身）
        title = data.get('title')
        if title:
            ValidationUtils.validate_uniqueness(
                Course, 'title', title, 
                exclude_id=self.instance.id,
                error_message=_("同名课程已存在，请使用不同的标题")
            )
        return data

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
    
    def validate_title(self, value):
        """验证知识点标题"""
        return ValidationUtils.validate_text_field(
            value, "title", min_length=2, max_length=100
        )
    
    def validate_importance(self, value):
        """验证重要性"""
        if not 1 <= value <= 10:
            raise serializers.ValidationError({"importance": _("重要性必须在1到10之间")})
        return value
    
    def validate_course(self, value):
        """验证课程存在"""
        if not value:
            raise serializers.ValidationError({"course": _("课程不能为空")})
        return value
    
    def validate(self, data):
        """验证创建数据"""
        # 确保parent知识点属于同一个课程
        parent = data.get('parent')
        course = data.get('course')
        
        if parent and course and parent.course != course:
            raise serializers.ValidationError(
                {"parent": _("父知识点必须属于同一个课程")}
            )
        
        # 验证同一课程下知识点标题唯一性
        title = data.get('title')
        if title and course:
            existing = KnowledgePoint.objects.filter(
                course=course, 
                title=title
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    {"title": _("同一课程中已存在同名知识点")}
                )
        
        return data


class KnowledgePointUpdateSerializer(serializers.ModelSerializer):
    """知识点更新序列化器"""
    
    class Meta:
        model = KnowledgePoint
        fields = ['title', 'content', 'importance', 'parent']
    
    def validate_title(self, value):
        """验证知识点标题"""
        return ValidationUtils.validate_text_field(
            value, "title", min_length=2, max_length=100
        )
    
    def validate_importance(self, value):
        """验证重要性"""
        if not 1 <= value <= 10:
            raise serializers.ValidationError({"importance": _("重要性必须在1到10之间")})
        return value
    
    def validate(self, data):
        """验证更新数据"""
        instance = self.instance
        
        # 确保parent知识点属于同一个课程
        parent = data.get('parent')
        if parent and instance.course != parent.course:
            raise serializers.ValidationError(
                {"parent": _("父知识点必须属于同一个课程")}
            )
        
        # 检查是否会形成循环引用
        if parent and self._would_create_cycle(instance, parent):
            raise serializers.ValidationError(
                {"parent": _("不能将知识点设为自己的子孙节点的父节点，这会形成循环引用")}
            )
        
        # 验证同一课程下知识点标题唯一性（排除自身）
        title = data.get('title')
        if title:
            existing = KnowledgePoint.objects.filter(
                course=instance.course, 
                title=title
            ).exclude(id=instance.id).exists()
            
            if existing:
                raise serializers.ValidationError(
                    {"title": _("同一课程中已存在同名知识点")}
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
    
    def validate_title(self, value):
        """验证课件标题"""
        return ValidationUtils.validate_text_field(
            value, "title", min_length=2, max_length=100
        )
    
    def validate_content(self, value):
        """验证课件内容"""
        return ValidationUtils.validate_text_field(
            value, "content", min_length=10
        )
    
    def validate_type(self, value):
        """验证课件类型"""
        valid_types = dict(Courseware.COURSEWARE_TYPES).keys()
        if value not in valid_types:
            raise serializers.ValidationError(
                _("无效的课件类型，可选值：{0}").format(", ".join(valid_types))
            )
        return value
    
    def validate_course(self, value):
        """验证课程存在"""
        if not value:
            raise serializers.ValidationError({"course": _("课程不能为空")})
        return value
    
    def validate(self, data):
        """验证创建数据"""
        # 验证同一课程下课件标题唯一性
        title = data.get('title')
        course = data.get('course')
        
        if title and course:
            existing = Courseware.objects.filter(
                course=course, 
                title=title
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    {"title": _("同一课程中已存在同名课件")}
                )
        
        return data
    
    def create(self, validated_data):
        # 设置当前请求用户为创建者
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CoursewareUpdateSerializer(serializers.ModelSerializer):
    """课件更新序列化器"""
    
    class Meta:
        model = Courseware
        fields = ['title', 'content', 'type']
    
    def validate_title(self, value):
        """验证课件标题"""
        return ValidationUtils.validate_text_field(
            value, "title", min_length=2, max_length=100
        )
    
    def validate_content(self, value):
        """验证课件内容"""
        return ValidationUtils.validate_text_field(
            value, "content", min_length=10
        )
    
    def validate_type(self, value):
        """验证课件类型"""
        valid_types = dict(Courseware.COURSEWARE_TYPES).keys()
        if value not in valid_types:
            raise serializers.ValidationError(
                _("无效的课件类型，可选值：{0}").format(", ".join(valid_types))
            )
        return value
    
    def validate(self, data):
        """验证更新数据"""
        instance = self.instance
        
        # 验证同一课程下课件标题唯一性（排除自身）
        title = data.get('title')
        if title:
            existing = Courseware.objects.filter(
                course=instance.course, 
                title=title
            ).exclude(id=instance.id).exists()
            
            if existing:
                raise serializers.ValidationError(
                    {"title": _("同一课程中已存在同名课件")}
                )
        
        return data 