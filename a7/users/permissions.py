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