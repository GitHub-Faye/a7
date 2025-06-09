from django.contrib import admin
from .models import WebhookConfig, WebhookCallLog


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    """Webhook配置管理界面"""
    list_display = ('name', 'url', 'active', 'created_at', 'updated_at')
    list_filter = ('active',)
    search_fields = ('name', 'url', 'description')


@admin.register(WebhookCallLog)
class WebhookCallLogAdmin(admin.ModelAdmin):
    """Webhook调用日志管理界面"""
    list_display = ('webhook', 'status', 'execution_time', 'created_at')
    list_filter = ('status', 'webhook')
    search_fields = ('webhook__name', 'error_message')
    readonly_fields = ('webhook', 'request_data', 'response_data', 'status', 
                      'error_message', 'execution_time', 'created_at')
