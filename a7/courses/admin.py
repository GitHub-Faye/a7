from django.contrib import admin
from .models import Course, KnowledgePoint, Courseware

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
