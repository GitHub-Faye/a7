from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.models import Permission
from django.db.models import Q

from users.models import Role

User = get_user_model()

class Command(BaseCommand):
    help = "同步用户的角色对象和权限，并创建默认角色"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("开始同步角色和权限..."))
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            # 创建默认角色
            self.create_default_roles()
            
            # 同步用户角色
            self.sync_user_roles()
            
        # 输出角色和用户统计信息
        self.show_statistics()
        
        self.stdout.write(self.style.SUCCESS("\n同步完成!"))
    
    def create_default_roles(self):
        """创建默认角色和权限"""
        self.stdout.write("创建默认角色...")
        
        # 管理员角色
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={'description': '管理员角色，拥有所有权限'}
        )
        admin_role.permissions.set(Permission.objects.all())
        
        # 教师角色
        teacher_role, created = Role.objects.get_or_create(
            name='teacher',
            defaults={'description': '教师角色，可以查看学生数据、管理课程和生成教学内容'}
        )
        # 设置教师权限
        teacher_perms = Permission.objects.filter(
            Q(codename='view_student_data') | 
            Q(codename='manage_courses') | 
            Q(codename='generate_teaching_content')
        )
        teacher_role.permissions.set(teacher_perms)
        
        # 学生角色
        student_role, created = Role.objects.get_or_create(
            name='student',
            defaults={'description': '学生角色，具有受限的基本访问权限'}
        )
        student_role.permissions.clear()
        
        self.stdout.write(self.style.SUCCESS(f"已创建或更新默认角色: admin, teacher, student"))
        
    def sync_user_roles(self):
        """同步用户角色，使用直接数据库更新避免触发信号"""
        self.stdout.write("同步用户角色...")
        
        # 获取所有角色
        roles = {role.name: role for role in Role.objects.all()}
        
        # 遍历所有用户
        total_users = User.objects.count()
        updated_count = 0
        
        for user in User.objects.all():
            updated = False
            
            # 如果用户有role但没有role_obj
            if user.role and not user.role_obj and user.role in roles:
                user.role_obj = roles[user.role]
                updated = True
                
            # 如果用户有role_obj但role不匹配
            elif user.role_obj and user.role != user.role_obj.name:
                user.role = user.role_obj.name
                updated = True
                
            # 如果需要更新，直接保存
            if updated:
                # 使用update_fields减少触发其他信号处理器的可能性
                user.save(update_fields=['role', 'role_obj'], syncing_roles=True)
                updated_count += 1
                
        self.stdout.write(self.style.SUCCESS(f"共处理 {total_users} 个用户，更新了 {updated_count} 个用户的角色"))
    
    def show_statistics(self):
        """显示角色和用户统计信息"""
        self.stdout.write("\n角色及关联用户统计:")
        
        for role in Role.objects.all():
            # 直接查询以避免触发额外的信号处理
            direct_user_count = User.objects.filter(role_obj=role).count()
            string_user_count = User.objects.filter(role=role.name).count()
            
            self.stdout.write(f"  - {role.name}: {direct_user_count} 个用户通过role_obj关联，{string_user_count} 个用户通过role字段关联") 