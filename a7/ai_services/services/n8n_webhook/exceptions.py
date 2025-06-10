"""
n8n Webhook异常模块

定义了与n8n Webhook交互过程中可能出现的各种异常类型
"""


class N8nWebhookError(Exception):
    """n8n Webhook服务基础异常类"""
    def __init__(self, message=None, *args, **kwargs):
        self.message = message or "n8n Webhook服务发生错误"
        self.status_code = kwargs.get('status_code', 500)
        self.response = kwargs.get('response')
        super().__init__(self.message, *args)

    def __str__(self):
        return f"{self.message} (状态码: {self.status_code})"


class N8nConnectionError(N8nWebhookError):
    """n8n Webhook连接异常"""
    def __init__(self, message=None, *args, **kwargs):
        message = message or "无法连接至n8n服务"
        super().__init__(message, *args, **kwargs)


class N8nTimeoutError(N8nWebhookError):
    """n8n Webhook请求超时异常"""
    def __init__(self, message=None, *args, **kwargs):
        message = message or "n8n服务请求超时"
        super().__init__(message, *args, **kwargs)


class N8nResponseError(N8nWebhookError):
    """n8n Webhook响应异常"""
    def __init__(self, message=None, *args, **kwargs):
        message = message or "n8n服务返回错误响应"
        super().__init__(message, *args, **kwargs)
        
        # 保存详细错误信息
        self.error_data = kwargs.get('error_data', {})
        self.validation_errors = kwargs.get('validation_errors', {})
        
    def __str__(self):
        base_str = super().__str__()
        if self.validation_errors:
            # 如果有验证错误，优先显示
            return f"{base_str}\n验证错误: {self.validation_errors}"
        if self.error_data:
            return f"{base_str}\n错误详情: {self.error_data}"
        return base_str


class N8nInvalidRequestError(N8nWebhookError):
    """n8n Webhook无效请求异常"""
    def __init__(self, message=None, *args, **kwargs):
        message = message or "无效的请求数据"
        # 默认为400 Bad Request
        kwargs.setdefault('status_code', 400)
        super().__init__(message, *args, **kwargs)
        
        # 保存详细的验证错误
        self.validation_errors = kwargs.get('validation_errors', {})
        
    def __str__(self):
        base_str = super().__str__()
        if self.validation_errors:
            return f"{base_str}\n验证错误: {self.validation_errors}"
        return base_str 