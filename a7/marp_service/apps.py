from django.apps import AppConfig


class MarpServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marp_service'
    verbose_name = 'Marp Presentation Service'
    
    def ready(self):
        """
        应用就绪时执行的代码
        可用于注册信号等初始化操作
        """
        # 暂时不需要任何初始化操作
        pass
