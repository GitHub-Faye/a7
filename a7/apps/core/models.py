from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
import json

class UsageStatistics(models.Model):
    """
    使用统计模型，记录用户在系统中的各种操作，便于后期分析使用模式
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='usage_statistics',
        verbose_name=_('用户')
    )
    module = models.CharField(
        max_length=50, 
        verbose_name=_('模块'),
        help_text=_('操作的模块，如course, exercise, learning_assistant')
    )
    action = models.CharField(
        max_length=50, 
        verbose_name=_('动作'),
        help_text=_('执行的动作，如view, create, submit')
    )
    details = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('详细信息'),
        help_text=_('以JSON格式存储的操作详情')
    )
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name=_('IP地址')
    )
    user_agent = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('用户代理'),
        help_text=_('浏览器和设备信息')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('时间戳')
    )
    
    class Meta:
        verbose_name = _('使用统计')
        verbose_name_plural = _('使用统计')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['module', 'action'], name='usage_mod_act_idx'),
            models.Index(fields=['user', 'timestamp'], name='usage_user_time_idx'),
            models.Index(fields=['ip_address'], name='usage_ip_idx')
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "已删除用户"
        return f"{user_str} - {self.module}.{self.action} - {self.timestamp}"
    
    def get_details_dict(self):
        """
        将details字段解析为Python字典
        """
        if not self.details:
            return {}
        try:
            return json.loads(self.details)
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON data'}


class PerformanceMetric(models.Model):
    """
    性能指标模型，存储系统的各种性能指标，用于监控和改进系统性能
    """
    METRIC_TYPES = (
        ('response_time', _('响应时间')),
        ('api_latency', _('API延迟')),
        ('resource_usage', _('资源使用')),
        ('error_rate', _('错误率')),
        ('active_users', _('活跃用户')),
        ('cpu_usage', _('CPU使用率')),
        ('memory_usage', _('内存使用率')),
        ('other', _('其他')),
    )
    
    metric_type = models.CharField(
        max_length=50,
        choices=METRIC_TYPES,
        verbose_name=_('指标类型')
    )
    value = models.FloatField(
        verbose_name=_('指标值')
    )
    unit = models.CharField(
        max_length=20,
        verbose_name=_('单位'),
        help_text=_('例如：ms, %, MB')
    )
    related_entity = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('关联实体'),
        help_text=_('特定API或资源的标识符')
    )
    context = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('上下文信息'),
        help_text=_('以JSON格式存储的额外上下文信息')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('时间戳')
    )
    
    class Meta:
        verbose_name = _('性能指标')
        verbose_name_plural = _('性能指标')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type'], name='perf_type_idx'),
            models.Index(fields=['related_entity'], name='perf_entity_idx'),
            models.Index(fields=['timestamp'], name='perf_time_idx')
        ]
    
    def __str__(self):
        return f"{self.metric_type} - {self.value}{self.unit} - {self.timestamp}"
    
    def get_context_dict(self):
        """
        将context字段解析为Python字典
        """
        if not self.context:
            return {}
        try:
            return json.loads(self.context)
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON data'} 