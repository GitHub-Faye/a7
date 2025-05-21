from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import Role
from .permission_utils import assign_role_permissions, update_user_permissions_on_role_change, sync_users_role_objects

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
    # 检查是否是使用syncing_roles进行的保存操作，如果是则跳过
    if kwargs.get('raw', False) or kwargs.get('update_fields') == ['role', 'role_obj']:
        return
        
    # 如果是新用户，则跳过，因为post_save信号处理函数会处理
    if instance.pk is None:
        return
        
    # 获取数据库中现有的用户数据
    try:
        old_instance = User.objects.get(pk=instance.pk)
        
        # 检查角色变化
        role_changed = old_instance.role != instance.role
        role_obj_changed = old_instance.role_obj != instance.role_obj
        
        # 如果role或role_obj发生了变化
        if role_changed or role_obj_changed:
            # 确定新的角色名称
            new_role = None
            if role_changed:
                new_role = instance.role
            elif role_obj_changed and instance.role_obj:
                new_role = instance.role_obj.name
                
            # 更新用户权限
            update_user_permissions_on_role_change(instance, old_instance.role, new_role)
    except User.DoesNotExist:
        pass  # 这是新用户，将由post_save信号处理


@receiver(post_save, sender=Role)
def update_role_users_permissions(sender, instance, created=False, **kwargs):
    """
    当角色权限更改时，更新所有使用该角色的用户的权限
    """
    # 获取所有使用此角色的用户（通过role字段或role_obj关联）
    users_by_role = User.objects.filter(role=instance.name)
    users_by_role_obj = User.objects.filter(role_obj=instance)
    
    # 合并用户集合
    users = users_by_role.union(users_by_role_obj)
    
    # 为每个用户更新权限
    for user in users:
        # 同步role和role_obj
        if user.role != instance.name or user.role_obj != instance:
            if user.role != instance.name:
                user.role = instance.name
            if user.role_obj != instance:
                user.role_obj = instance
            user.save(syncing_roles=True, update_fields=['role', 'role_obj'])
        
        # 分配权限
        assign_role_permissions(user)
        
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def sync_user_role_objects(sender, instance=None, created=False, **kwargs):
    """
    确保用户的role和role_obj始终保持同步
    """
    # 检查是否是使用syncing_roles进行的保存操作，如果是则跳过
    if kwargs.get('raw', False) or kwargs.get('syncing_roles', False) or created:
        return
        
    # 跳过信号递归和创建步骤的处理(创建由其他信号处理)
    if kwargs.get('update_fields') == ['role', 'role_obj']:
        return
        
    # 尝试同步role和role_obj
    if instance.role and not instance.role_obj:
        # 用户有role但没有role_obj，尝试找到对应的Role对象
        try:
            role = Role.objects.get(name=instance.role)
            instance.role_obj = role
            instance.save(syncing_roles=True, update_fields=['role_obj'])
        except Role.DoesNotExist:
            pass
    elif instance.role_obj and instance.role != instance.role_obj.name:
        # 用户有role_obj但role不匹配，更新role
        instance.role = instance.role_obj.name
        instance.save(syncing_roles=True, update_fields=['role']) 