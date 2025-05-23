from rest_framework import permissions

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    只允许教师或管理员访问
    """
    def has_permission(self, request, view):
        # 检查用户是否已登录
        if not request.user or not request.user.is_authenticated:
            return False

        # 检查用户是否是管理员或者教师
        return request.user.is_staff or request.user.role == 'teacher'


class IsCourseTeacherOrAdmin(permissions.BasePermission):
    """
    只允许课程创建者(教师)或管理员修改课程
    """
    def has_object_permission(self, request, view, obj):
        # 检查用户是否已登录
        if not request.user or not request.user.is_authenticated:
            return False

        # 管理员始终有权限
        if request.user.is_staff:
            return True

        # 检查用户是否是课程的创建者
        return obj.teacher == request.user 