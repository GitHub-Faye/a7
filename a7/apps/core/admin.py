from django.contrib import admin
from .models import UsageStatistics, PerformanceMetric

@admin.register(UsageStatistics)
class UsageStatisticsAdmin(admin.ModelAdmin):
    """管理使用统计的Admin配置"""
    list_display = ('user', 'module', 'action', 'timestamp', 'ip_address')
    list_filter = ('module', 'action', 'timestamp')
    search_fields = ('user__username', 'user__email', 'module', 'action', 'details')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'module', 'action')
        }),
        ('详细信息', {
            'fields': ('details', 'ip_address', 'user_agent')
        }),
        ('时间信息', {
            'fields': ('timestamp',)
        }),
    )

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    """管理性能指标的Admin配置"""
    list_display = ('metric_type', 'value', 'unit', 'related_entity', 'timestamp')
    list_filter = ('metric_type', 'unit', 'timestamp')
    search_fields = ('metric_type', 'related_entity', 'context')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        (None, {
            'fields': ('metric_type', 'value', 'unit')
        }),
        ('关联信息', {
            'fields': ('related_entity', 'context')
        }),
        ('时间信息', {
            'fields': ('timestamp',)
        }),
    ) 