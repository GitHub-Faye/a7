from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import _user_get_permissions


class User(AbstractUser):
    """
    扩展Django默认用户模型，添加角色字段
    """
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('teacher', '教师'),
        ('student', '学生'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        permissions = (
            ('view_student_data', '查看学生数据'),
            ('manage_courses', '管理课程'),
            ('generate_teaching_content', '生成教学内容'),
        )
    
    def __str__(self):
        return self.username
        
    def has_perm(self, perm, obj=None):
        """
        检查用户是否具有特定权限。
        如果用户是管理员角色，则返回True。
        否则，检查用户是否具有特定权限。
        """
        # 如果用户是超级用户，则拥有所有权限
        if self.is_superuser:
            return True
            
        # 如果用户是管理员角色，则拥有所有权限
        if self.role == 'admin':
            return True
            
        # 否则，检查用户是否具有特定权限
        if not self.is_active:
            return False
            
        # 权限格式可能是app.codename或直接是codename
        if '.' in perm:
            app_label, codename = perm.split('.')
        else:
            app_label, codename = None, perm
        
        # 首先检查用户的User.user_permissions
        if self.user_permissions.filter(codename=codename).exists():
            return True
            
        # 然后检查用户所属的组的权限
        for group in self.groups.all():
            if group.permissions.filter(codename=codename).exists():
                return True
        
        # 最后，为特定角色添加硬编码的权限规则
        if self.role == 'teacher':
            teacher_perms = ['view_student_data', 'manage_courses', 'generate_teaching_content']
            if codename in teacher_perms:
                return True
                
        # 学生等其他角色默认没有特殊权限
        return False
        
    def has_module_perms(self, app_label):
        """
        检查用户是否有某个app的权限
        """
        # 超级用户和管理员拥有所有模块的权限
        if self.is_superuser or self.role == 'admin':
            return True
            
        # 检查用户是否有app中的任何权限
        if not self.is_active:
            return False
            
        # 获取用户的所有权限
        user_perms = self.user_permissions.filter(content_type__app_label=app_label).exists()
        if user_perms:
            return True
            
        # 检查用户组的权限
        for group in self.groups.all():
            if group.permissions.filter(content_type__app_label=app_label).exists():
                return True
                
        # 为特定角色添加硬编码的应用权限
        if app_label == 'users' and self.role in ['admin', 'teacher']:
            return True
            
        return False


class Role(models.Model):
    """
    角色模型，用于更精细的权限控制
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    description = models.TextField(blank=True, verbose_name='角色描述')
    permissions = models.ManyToManyField(
        Permission, 
        blank=True, 
        related_name='roles',
        verbose_name='权限'
    )
    
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
    
    def __str__(self):
        return self.name
