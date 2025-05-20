from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from users.permission_utils import sync_role_permissions, assign_role_permissions

User = get_user_model()

class Command(BaseCommand):
    help = '初始化角色和权限，同时更新现有用户的权限'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='强制重置所有角色和权限',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        with transaction.atomic():
            # 同步角色和权限
            roles = sync_role_permissions()
            self.stdout.write(self.style.SUCCESS('√ 角色和权限同步成功'))
            
            # 打印角色信息
            for role_name, role in roles.items():
                perm_count = role.permissions.count()
                self.stdout.write(
                    self.style.SUCCESS(f'- {role_name}: {role.description} ({perm_count}个权限)')
                )
            
            # 更新用户权限
            users = User.objects.all()
            updated_count = 0
            
            for user in users:
                # 如果强制更新或用户没有任何权限
                if force or not user.user_permissions.exists():
                    result = assign_role_permissions(user)
                    if result:
                        updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'√ 已更新{updated_count}/{users.count()}个用户的权限')
            ) 