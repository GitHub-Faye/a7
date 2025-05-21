from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Q

from .models import User, Role
from .permission_utils import sync_role_permissions


class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'role', 'get_role_obj', 'is_staff', 'is_active')
    list_filter = ('role', 'role_obj', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Role info'), {'fields': ('role', 'role_obj')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'role_obj', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    def get_role_obj(self, obj):
        """显示用户的role_obj对象名称"""
        return obj.role_obj.name if obj.role_obj else '-'
    
    get_role_obj.short_description = '角色对象'
    
    def save_model(self, request, obj, form, change):
        """保存模型时，确保role和role_obj保持同步"""
        role_changed = change and 'role' in form.changed_data
        role_obj_changed = change and 'role_obj' in form.changed_data
        
        # 如果两者都没变，或两者都发生了变化，则正常保存
        if (not role_changed and not role_obj_changed) or (role_changed and role_obj_changed):
            super().save_model(request, obj, form, change)
            return
            
        # 如果只有role变化了，但role_obj没变
        if role_changed and not role_obj_changed:
            try:
                role_obj = Role.objects.get(name=obj.role)
                obj.role_obj = role_obj
                messages.info(request, f'已自动设置角色对象: {role_obj.name}')
            except Role.DoesNotExist:
                messages.warning(request, f'找不到名为"{obj.role}"的角色对象，role_obj值未更新')
        
        # 如果只有role_obj变化了，但role没变
        elif not role_changed and role_obj_changed:
            if obj.role_obj:
                obj.role = obj.role_obj.name
                messages.info(request, f'已自动设置角色: {obj.role}')
        
        super().save_model(request, obj, form, change)


class RoleAdmin(admin.ModelAdmin):
    """角色管理界面"""
    list_display = ('name', 'description', 'get_permissions_count', 'get_users_count')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)
    actions = ['sync_users_with_this_role']
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    
    get_permissions_count.short_description = '权限数量'
    
    def get_users_count(self, obj):
        return obj.users.count()
    
    get_users_count.short_description = '用户数量'
    
    def sync_users_with_this_role(self, request, queryset):
        """同步选定角色的所有用户的权限"""
        for role in queryset:
            users_updated = 0
            # 更新使用此角色的所有用户
            for user in User.objects.filter(role_obj=role):
                user.user_permissions.set(role.permissions.all())
                users_updated += 1
            
            # 同时更新使用角色名称但未设置role_obj的用户
            for user in User.objects.filter(role=role.name, role_obj__isnull=True):
                user.role_obj = role
                user.user_permissions.set(role.permissions.all())
                user.save(syncing_roles=True)
                users_updated += 1
                
            self.message_user(
                request,
                f'已同步角色 "{role.name}" 的权限到 {users_updated} 个用户。',
                messages.SUCCESS
            )
    
    sync_users_with_this_role.short_description = "同步所选角色的权限到用户"
    
    def save_model(self, request, obj, form, change):
        """保存模型时同步权限"""
        super().save_model(request, obj, form, change)
        
        # 如果权限发生了变化，同步到所有使用此角色的用户
        if change and 'permissions' in form.changed_data:
            users_count = 0
            # 更新使用此角色的所有用户
            for user in User.objects.filter(Q(role_obj=obj) | Q(role=obj.name)):
                user.user_permissions.set(obj.permissions.all())
                users_count += 1
                
            messages.info(request, f'已同步角色权限到 {users_count} 个用户')


class PermissionAdmin(admin.ModelAdmin):
    """权限管理界面"""
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type',)
    search_fields = ('name', 'codename')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
# 添加Django自带的权限模型到admin页面，方便管理员查看
from django.contrib.auth.models import Permission
admin.site.register(Permission, PermissionAdmin)

# 添加批量操作按钮
admin.site.add_action(sync_role_permissions, '同步所有角色和权限')
