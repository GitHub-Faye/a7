from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import Role
from .permission_utils import assign_role_permissions, update_user_permissions_on_role_change

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    为新创建的用户自动创建Token
    """
    if created:
        # 如果settings中配置了rest_framework.authtoken
        if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
            Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_permissions(sender, instance, created, **kwargs):
    """
    当用户创建时，为其分配基于角色的权限
    """
    if created:
        # 为新用户分配其角色对应的权限
        assign_role_permissions(instance)


@receiver(pre_save, sender=User)
def update_user_role_permissions(sender, instance, **kwargs):
    """
    当用户角色变更时，更新其权限
    """
    # 如果是新用户，则跳过，因为post_save信号处理函数会处理
    if instance.pk is None:
        return
        
    # 获取数据库中现有的用户数据
    try:
        old_instance = User.objects.get(pk=instance.pk)
        # 如果角色已更改，则更新权限
        if old_instance.role != instance.role:
            update_user_permissions_on_role_change(instance, old_instance.role, instance.role)
    except User.DoesNotExist:
        pass  # 这是新用户，将由post_save信号处理


@receiver(post_save, sender=Role)
def update_role_users_permissions(sender, instance, **kwargs):
    """
    当角色权限更改时，更新所有使用该角色的用户的权限
    """
    # 获取所有使用此角色的用户
    users = User.objects.filter(role=instance.name)
    
    # 为每个用户更新权限
    for user in users:
        assign_role_permissions(user) 