from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = '用户管理'
    
    def ready(self):
        # 导入信号处理器
        import users.signals
