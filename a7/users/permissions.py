from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    只允许管理员执行写操作，其他用户只能读
    """
    
    def has_permission(self, request, view):
        # 读操作允许任何已认证的用户
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 写操作只允许管理员
        return request.user and request.user.is_staff


class IsUserOwnerOrStaff(permissions.BasePermission):
    """
    只允许用户操作自己的数据，或者管理员操作任何数据
    """
    
    def has_object_permission(self, request, view, obj):
        # 管理员可以执行任何操作
        if request.user.is_staff:
            return True
        
        # 普通用户只能操作自己的数据
        return obj == request.user

# 新增的基于角色的权限类

class IsAdmin(permissions.BasePermission):
    """
    只允许管理员角色的用户访问
    """
    message = '只有管理员才能执行此操作。'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(permissions.BasePermission):
    """
    只允许教师角色的用户访问
    """
    message = '只有教师才能执行此操作。'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsStudent(permissions.BasePermission):
    """
    只允许学生角色的用户访问
    """
    message = '只有学生才能执行此操作。'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsAdminOrTeacher(permissions.BasePermission):
    """
    允许管理员或教师角色的用户访问
    """
    message = '只有管理员或教师才能执行此操作。'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'teacher']


class HasViewStudentDataPermission(permissions.BasePermission):
    """
    允许有查看学生数据权限的用户访问
    """
    message = '没有查看学生数据的权限。'

    def has_permission(self, request, view):
        return request.user.has_perm('users.view_student_data')


class HasManageCoursesPermission(permissions.BasePermission):
    """
    允许有管理课程权限的用户访问
    """
    message = '没有管理课程的权限。'

    def has_permission(self, request, view):
        return request.user.has_perm('users.manage_courses')


class HasGenerateTeachingContentPermission(permissions.BasePermission):
    """
    允许有生成教学内容权限的用户访问
    """
    message = '没有生成教学内容的权限。'

    def has_permission(self, request, view):
        return request.user.has_perm('users.generate_teaching_content')


class IsTeacherWithCourseManagement(permissions.BasePermission):
    """
    要求用户是教师且拥有课程管理权限
    """
    message = '需要教师角色和课程管理权限。'

    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role == 'teacher' and 
                request.user.has_perm('users.manage_courses'))


class IsAdminOrTeacherReadOnly(permissions.BasePermission):
    """
    管理员拥有读写权限，教师只有读权限
    """
    message = '只有管理员可以修改数据，教师只能查看数据。'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # 管理员可以执行任何操作
        if request.user.role == 'admin':
            return True
            
        # 教师只能执行读操作
        if request.user.role == 'teacher':
            return request.method in permissions.SAFE_METHODS
            
        return False 