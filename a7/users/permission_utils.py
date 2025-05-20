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
    return True


def assign_student_permissions(user):
    """为学生用户分配基本权限"""
    # 学生通常只需要非常基本的权限
    user.user_permissions.clear()
    return True


def get_user_role_permissions(user):
    """获取用户基于角色的所有权限"""
    # 获取用户的直接权限
    direct_perms = user.user_permissions.all()
    
    # 获取用户通过组获得的权限
    group_perms = Permission.objects.filter(group__user=user)
    
    # 合并所有权限
    all_perms = direct_perms | group_perms
    
    return all_perms.distinct()


def sync_role_permissions():
    """
    同步角色和权限的关系
    更新所有角色对象中的权限设置
    """
    # 获取角色相关权限
    view_student_data = get_permission_by_codename('view_student_data')
    manage_courses = get_permission_by_codename('manage_courses')
    generate_teaching_content = get_permission_by_codename('generate_teaching_content')
    
    # 更新或创建管理员角色
    admin_role, created = Role.objects.get_or_create(name='admin')
    admin_role.description = '管理员角色，拥有所有权限'
    admin_role.permissions.set(Permission.objects.all())
    admin_role.save()
    
    # 更新或创建教师角色
    teacher_role, created = Role.objects.get_or_create(name='teacher')
    teacher_role.description = '教师角色，可以查看学生数据、管理课程和生成教学内容'
    teacher_perms = [p for p in [view_student_data, manage_courses, generate_teaching_content] if p]
    teacher_role.permissions.set(teacher_perms)
    teacher_role.save()
    
    # 更新或创建学生角色
    student_role, created = Role.objects.get_or_create(name='student')
    student_role.description = '学生角色，具有受限的基本访问权限'
    student_role.permissions.clear()
    student_role.save()
    
    return {
        'admin': admin_role,
        'teacher': teacher_role,
        'student': student_role
    }


def update_user_permissions_on_role_change(user, old_role=None, new_role=None):
    """当用户角色变更时更新其权限"""
    if new_role:
        return assign_role_permissions(user, new_role)
    return assign_role_permissions(user) 