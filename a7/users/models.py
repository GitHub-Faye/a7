from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


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
