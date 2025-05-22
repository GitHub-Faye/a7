from django.contrib import admin
from .models import Course, KnowledgePoint, Courseware, Exercise, StudentAnswer, LearningRecord

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade_level', 'teacher', 'created_at')
    list_filter = ('subject', 'grade_level', 'teacher')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'importance', 'parent')
    list_filter = ('course', 'importance')
    search_fields = ('title', 'content')
    raw_id_fields = ('course', 'parent')

@admin.register(Courseware)
class CoursewareAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'type', 'created_by', 'created_at')
    list_filter = ('course', 'type', 'created_by')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    raw_id_fields = ('course', 'created_by')

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'knowledge_point', 'type', 'difficulty', 'created_at')
    list_filter = ('type', 'difficulty', 'knowledge_point__course')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    raw_id_fields = ('knowledge_point',)

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'exercise', 'score', 'submitted_at')
    list_filter = ('exercise__type', 'student', 'exercise__knowledge_point__course')
    search_fields = ('content', 'feedback', 'student__username', 'exercise__title')
    date_hierarchy = 'submitted_at'
    raw_id_fields = ('student', 'exercise')

@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'knowledge_point', 'status', 'progress', 'time_spent', 'last_accessed')
    list_filter = ('status', 'course', 'student')
    search_fields = ('student__username', 'course__title', 'knowledge_point__title')
    date_hierarchy = 'last_accessed'
    raw_id_fields = ('student', 'course', 'knowledge_point')
    
    fieldsets = (
        (None, {
            'fields': ('student', 'course', 'knowledge_point')
        }),
        ('学习状态', {
            'fields': ('status', 'progress', 'time_spent')
        }),
        ('时间信息', {
            'fields': ('last_accessed', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_accessed')
