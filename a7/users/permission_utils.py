from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import User, Role


def get_permission_by_codename(codename):
    """获取指定代码名称的权限对象"""
    try:
        return Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        return None


def assign_role_permissions(user, role_name=None):
    """
    根据用户角色分配相应权限
    如果指定了role_name，则使用该角色名称；否则使用用户当前角色
    """
    if not role_name:
        role_name = user.role
        
    # 尝试获取对应的Role对象
    try:
        role = Role.objects.get(name=role_name)
        # 设置用户的role_obj
        if user.role_obj != role:
            user.role_obj = role
            user.save(syncing_roles=True)  # 使用syncing_roles=True避免循环引用
    except Role.DoesNotExist:
        # 如果找不到对应的Role对象，尝试创建
        if role_name in dict(User.ROLE_CHOICES).keys():
            role = create_default_role(role_name)
            if user.role_obj != role:
                user.role_obj = role
                user.save(syncing_roles=True)  # 使用syncing_roles=True避免循环引用
        
    if role_name == 'admin':
        # 管理员拥有所有权限
        return assign_admin_permissions(user)
    elif role_name == 'teacher':
        # 教师拥有特定权限
        return assign_teacher_permissions(user)
    elif role_name == 'student':
        # 学生拥有最少的权限
        return assign_student_permissions(user)
    
    return False


def assign_admin_permissions(user):
    """为管理员用户分配所有权限"""
    # 获取所有权限
    permissions = Permission.objects.all()
    # 分配所有权限
    user.user_permissions.set(permissions)
    
    # 同步到role_obj（如果存在）
    if user.role_obj:
        user.role_obj.permissions.set(permissions)
    
    return True


def assign_teacher_permissions(user):
    """为教师用户分配教学相关权限"""
    # 获取教师所需的特定权限
    permissions = Permission.objects.filter(
        Q(codename='view_student_data') | 
        Q(codename='manage_courses') | 
        Q(codename='generate_teaching_content')
    )
    # 分配这些权限
    user.user_permissions.set(permissions)
    
    # 同步到role_obj（如果存在）
    if user.role_obj:
        user.role_obj.permissions.set(permissions)
    
    return True


def assign_student_permissions(user):
    """为学生用户分配基本权限"""
    # 学生通常只需要非常基本的权限
    user.user_permissions.clear()
    
    # 同步到role_obj（如果存在）
    if user.role_obj:
        user.role_obj.permissions.clear()
    
    return True


def get_user_role_permissions(user):
    """获取用户基于角色的所有权限"""
    # 获取用户的直接权限
    direct_perms = user.user_permissions.all()
    
    # 获取用户通过组获得的权限
    group_perms = Permission.objects.filter(group__user=user)
    
    # 获取用户通过role_obj获得的权限（如果存在）
    role_perms = Permission.objects.none()
    if user.role_obj:
        role_perms = user.role_obj.permissions.all()
    
    # 合并所有权限
    all_perms = direct_perms | group_perms | role_perms
    
    return all_perms.distinct()


def create_default_role(role_name):
    """创建默认角色"""
    if role_name == 'admin':
        role, created = Role.objects.get_or_create(
            name='admin',
            defaults={
                'description': '管理员角色，拥有所有权限'
            }
        )
        if created:
            role.permissions.set(Permission.objects.all())
    
    elif role_name == 'teacher':
        role, created = Role.objects.get_or_create(
            name='teacher',
            defaults={
                'description': '教师角色，可以查看学生数据、管理课程和生成教学内容'
            }
        )
        if created:
            perms = Permission.objects.filter(
                Q(codename='view_student_data') | 
                Q(codename='manage_courses') | 
                Q(codename='generate_teaching_content')
            )
            role.permissions.set(perms)
    
    elif role_name == 'student':
        role, created = Role.objects.get_or_create(
            name='student',
            defaults={
                'description': '学生角色，具有受限的基本访问权限'
            }
        )
        # 学生默认没有特殊权限
    
    else:
        # 创建自定义角色
        role, created = Role.objects.get_or_create(
            name=role_name,
            defaults={
                'description': f'自定义角色: {role_name}'
            }
        )
    
    return role


def sync_role_permissions(modeladmin, request, queryset=None):
    """
    同步所有角色和权限的admin操作函数
    """
    # 创建默认角色
    admin_role = create_default_role('admin')
    admin_role.permissions.set(Permission.objects.all())
    
    teacher_role = create_default_role('teacher')
    teacher_perms = Permission.objects.filter(
        Q(codename='view_student_data') | 
        Q(codename='manage_courses') | 
        Q(codename='generate_teaching_content')
    )
    teacher_role.permissions.set(teacher_perms)
    
    student_role = create_default_role('student')
    student_role.permissions.clear()
    
    # 同步用户角色
    roles = {role.name: role for role in Role.objects.all()}
    users_updated = 0
    
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
            user.save(syncing_roles=True)
            users_updated += 1
    
    if request:
        from django.contrib import messages
        messages.success(request, f'已同步角色权限，更新了 {users_updated} 个用户的角色。')
        
    return {
        'admin': admin_role,
        'teacher': teacher_role,
        'student': student_role
    }


def sync_users_role_objects():
    """同步所有用户的role和role_obj"""
    # 获取所有角色
    roles = {role.name: role for role in Role.objects.all()}
    
    # 获取所有用户
    users = User.objects.all()
    
    for user in users:
        # 如果用户有role但没有role_obj
        if user.role and not user.role_obj:
            # 尝试找到对应的Role对象
            if user.role in roles:
                user.role_obj = roles[user.role]
                user.save(syncing_roles=True)  # 使用syncing_roles=True避免循环引用
        # 如果用户有role_obj但role不匹配
        elif user.role_obj and user.role != user.role_obj.name:
            user.role = user.role_obj.name
            user.save(syncing_roles=True)  # 使用syncing_roles=True避免循环引用


def update_user_permissions_on_role_change(user, old_role=None, new_role=None):
    """当用户角色变更时更新其权限"""
    if new_role:
        return assign_role_permissions(user, new_role)
    return assign_role_permissions(user) 