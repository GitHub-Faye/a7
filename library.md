# Context7库IDs

| 库名 | Context7 ID | 说明 |
|------|-------------|------|
| Django REST Framework | /encode/django-rest-framework | Django的REST API框架 |
| djangorestframework-simplejwt | /jazzband/djangorestframework-simplejwt | JWT认证框架 |
| django-cors-headers | N/A (通过web_search获取) | CORS跨域资源共享框架 |
| drf-yasg | N/A (通过web_search获取) | Swagger/OpenAPI自动文档生成工具 |
| Django | /django/django | Python Web框架 |
| pytest-django | /pytest-dev/pytest-django | Django测试工具 |

# 主要库功能说明

## Django REST Framework
- 提供ModelSerializer简化模型序列化
- 视图集(ViewSet)支持CRUD操作
- 权限类控制API访问权限
- 支持各种认证方式
- 提供@action装饰器用于自定义API端点（如密码更改）
- 支持序列化器验证和字段定制（如密码验证）
- 包含APITestCase和APIClient类用于API测试

## djangorestframework-simplejwt
- 提供JWT认证功能
- 支持令牌刷新
- 令牌黑名单功能
- 可自定义令牌内容
- 与Django用户认证系统集成，支持密码管理
- 提供令牌验证视图和黑名单功能

## Django权限与角色系统
- Django自带权限系统(Permission)支持细粒度权限控制
- 自定义Role模型实现基于角色的权限管理
- User与Role外键关系支持多角色场景
- 权限继承与聚合（用户直接权限、组权限、角色权限）
- 信号处理同步用户角色与权限
- Django Admin集成的权限管理界面
- 支持角色权限批量同步和更新
- 管理命令实现角色权限初始化和同步
- 向后兼容性设计，同时支持字符串角色和对象引用

## Django测试工具
- Django TestCase提供数据库重置和事务支持
- pytest-django增强Django测试功能
- APITestCase专门用于REST API测试
- APIClient用于模拟API请求
- 支持测试认证和权限功能
- 提供强大的断言工具验证响应

## 主要依赖库版本

| 库名 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.x | Web框架 |
| djangorestframework | 3.14.x | REST API框架 |
| djangorestframework-simplejwt | 5.x | JWT认证 |
| drf-yasg | 1.21.x | API文档 |
| django-cors-headers | 4.x | CORS支持 |
| pytest-django | 4.5.x | Django测试扩展 |


```
