from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    verbose_name = '课程管理'
    
    def ready(self):
        """应用准备就绪时注册信号处理器"""
        import courses.signals  # 导入信号处理器
