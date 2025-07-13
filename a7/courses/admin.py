from django.contrib import admin
from .models import Course, KnowledgePoint, Courseware, Exercise, StudentAnswer, LearningRecord, CourseProgress

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade_level', 'teacher', 'created_at')
    list_filter = ('subject', 'grade_level', 'teacher')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'importance', 'parent', 'is_required', 'estimated_time')
    list_filter = ('course', 'importance', 'is_required')
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
    list_display = ('title', 'knowledge_point', 'type', 'difficulty', 'is_required', 
                   'correct_count', 'attempt_count', 'get_correctness_rate', 'created_at')
    list_filter = ('type', 'difficulty', 'knowledge_point__course', 'is_required')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    raw_id_fields = ('knowledge_point',)
    
    def get_correctness_rate(self, obj):
        return f"{obj.correctness_rate:.1f}%" if obj.attempt_count > 0 else "0.0%"
    get_correctness_rate.short_description = '正确率'

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'exercise', 'score', 'is_correct', 'attempt_count', 'submitted_at')
    list_filter = ('exercise__type', 'student', 'exercise__knowledge_point__course', 'is_correct')
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

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'overall_progress', 'required_completed', 
                    'correctness_rate', 'total_time_spent', 'is_completed', 'completion_date')
    list_filter = ('course', 'student', 'is_completed', 'required_completed')
    search_fields = ('student__username', 'course__title')
    date_hierarchy = 'last_activity'
    raw_id_fields = ('student', 'course')
    
    fieldsets = (
        (None, {
            'fields': ('student', 'course')
        }),
        ('进度信息', {
            'fields': ('overall_progress', 'required_completed', 'correctness_rate', 'total_time_spent')
        }),
        ('完成状态', {
            'fields': ('is_completed', 'completion_date')
        }),
        ('时间信息', {
            'fields': ('last_activity',)
        }),
    )
    readonly_fields = ('last_activity', )
