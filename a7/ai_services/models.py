from django.db import models
from django.utils.translation import gettext_lazy as _


class WebhookConfig(models.Model):
    """n8n Webhook配置模型"""
    name = models.CharField(_("名称"), max_length=100)
    description = models.TextField(_("描述"), blank=True, null=True)
    url = models.URLField(_("Webhook URL"), max_length=255)
    headers = models.JSONField(_("请求头"), default=dict, blank=True)
    active = models.BooleanField(_("是否启用"), default=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    
    class Meta:
        verbose_name = _("Webhook配置")
        verbose_name_plural = _("Webhook配置")
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.name


class WebhookCallLog(models.Model):
    """Webhook调用日志模型"""
    STATUS_CHOICES = (
        ("success", _("成功")),
        ("error", _("错误")),
        ("pending", _("处理中")),
    )
    
    webhook = models.ForeignKey(
        WebhookConfig, 
        related_name="call_logs",
        on_delete=models.CASCADE,
        verbose_name=_("Webhook配置")
    )
    request_data = models.JSONField(_("请求数据"), default=dict)
    response_data = models.JSONField(_("响应数据"), default=dict, null=True, blank=True)
    status = models.CharField(_("状态"), max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(_("错误信息"), blank=True, null=True)
    execution_time = models.FloatField(_("执行时间(秒)"), null=True, blank=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Webhook调用日志")
        verbose_name_plural = _("Webhook调用日志")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.webhook.name} - {self.created_at} - {self.status}"
