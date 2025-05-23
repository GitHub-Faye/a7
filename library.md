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
- 支持Swagger/OpenAPI文档集成与自动生成

## djangorestframework-simplejwt
- 提供JWT认证功能
- 支持令牌刷新
- 令牌黑名单功能
- 可自定义令牌内容
- 与Django用户认证系统集成，支持密码管理
- 提供令牌验证视图和黑名单功能
- 包含TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView视图类
- 令牌响应格式自定义功能
- 可扩展的令牌类与验证
- 提供JWTAuthentication认证类供中间件使用
- 异常处理类(InvalidToken, TokenError, AuthenticationFailed)用于令牌验证
- 支持过期令牌检测和自定义错误响应

## Django中间件系统
- 提供请求/响应处理的中间件架构
- 支持自定义中间件类的创建与配置
- 中间件执行顺序可通过MIDDLEWARE设置控制
- 提供MiddlewareMixin简化中间件实现
- 支持请求前处理和响应后处理
- 可访问和修改请求和响应对象
- 支持中间件链式处理和短路返回
- 支持异常处理和请求拦截
- 可用于实现认证、日志记录、内容处理等功能
- 与Django日志系统集成，支持详细日志记录
- 提供settings.py中的配置选项自定义中间件行为

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

## Django模型与JSON字段处理
- TextField用于存储JSON格式数据
- json.loads/dumps处理JSON字符串与Python对象转换
- 自定义方法处理JSON解析错误和边缘情况
- try/except结构确保JSON解析的健壮性
- 模型方法封装复杂的JSON字段操作
- 对空值和无效JSON提供合理的默认行为
- 支持复杂嵌套结构，如列表、字典和混合类型
- 通过Meta.indexes优化JSON相关字段的查询性能

## Django测试工具
- Django TestCase提供数据库重置和事务支持
- pytest-django增强Django测试功能
- APITestCase专门用于REST API测试
- APIClient用于模拟API请求
- 支持测试认证和权限功能
- 提供强大的断言工具验证响应
- IntegrityError异常用于测试唯一性和约束条件
- TestCase支持测试模型间关系和数据完整性
- 支持数据库索引和约束的测试
- 模拟环境支持设置特定时间和环境变量
- 支持测试时间相关功能（如排序和过滤）
- assertAlmostEqual用于测试浮点数计算
- filter和exclude方法用于测试数据查询
- values_list用于提取特定字段数据进行测试
- TestCase.setUp和TestCase.tearDown支持测试环境准备和清理
- self.client用于HTTP请求测试
- 列表解析和过滤用于测试复杂逻辑
- unittest.mock提供强大的模拟功能，如patch和MagicMock
- 支持中间件单元测试和集成测试
- RequestFactory用于创建HTTP请求对象用于测试

## 主要依赖库版本

| 库名 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.x | Web框架 |
| djangorestframework | 3.14.x | REST API框架 |
| djangorestframework-simplejwt | 5.x | JWT认证 |
| drf-yasg | 1.21.x | API文档 |
| django-cors-headers | 4.x | CORS支持 |
| pytest-django | 4.5.x | Django测试扩展 |

## Django模型关系和测试技术

### 模型关系类型
- ForeignKey: 一对多关系（如User-UsageStatistics, Course-KnowledgePoint）
- ManyToManyField: 多对多关系（如用户权限分配）
- OneToOneField: 一对一关系
- 自引用外键: 层次结构（如KnowledgePoint的parent字段）

### 高级查询技术
- select_related/prefetch_related: 优化关联查询
- annotate/aggregate: 聚合和计算
- F表达式: 字段引用和操作
- Q对象: 复杂条件查询
- values/values_list: 获取特定字段

### 测试最佳实践
- 使用setUp准备测试数据
- 模拟实际使用场景进行端到端测试
- 测试边缘情况和异常处理
- 使用list()和order_by()确保测试查询结果的确定性
- 利用断言方法验证预期结果
- 使用django.utils.timezone模拟时间相关功能
- 使用具体值而非计算值进行测试比较
- 明确测试目标和期望结果
- 给每个测试方法编写清晰的文档说明
- 遵循独立性原则，测试之间不应相互依赖

### 学习进度跟踪模型测试技术
- 测试状态转换逻辑
- 验证进度更新和时间累计功能
- 测试模型属性和辅助方法
- 模拟真实学习过程进行端到端测试
- 验证统计计算的准确性
- 测试唯一约束和数据完整性

### 级联删除策略最佳实践
- 对关键用户数据关联使用SET_NULL，避免删除用户时丢失重要数据
- 对内容层次结构使用CASCADE，保持数据一致性
- 使用on_delete=PROTECT保护不能轻易删除的关键数据
- 对每个外键关系谨慎选择级联策略，考虑数据完整性和业务规则
- 为每个级联策略编写专门的测试用例验证行为
- 考虑使用soft delete（软删除）代替硬删除来保留数据历史

### 数据库索引优化技术
- 为频繁查询的字段添加索引提高性能
- 组合字段索引优化多字段查询（如Course的subject+grade_level索引）
- 遵循有意义的索引命名约定（如kp_course_imp_idx, lr_progress_idx）
- 避免过度索引导致写入性能下降
- 考虑使用部分索引减少索引大小（Django 3.2+支持）
- 使用unique_together和UniqueConstraint实现多字段唯一性
- 为复杂查询创建特定索引（如多列索引或包含索引）

### 模型关系测试策略
- 测试级联删除行为（删除父记录后验证子记录状态）
- 测试SET_NULL关系（删除关联记录后验证字段被设为null）
- 验证多对多关系的操作（添加、删除和关联）
- 测试唯一性约束（尝试创建重复记录应引发IntegrityError）
- 验证反向关系查询（如通过related_name访问）
- 测试复杂的多级级联删除场景
- 使用独立的测试方法和事务隔离确保测试纯净性
- 确保测试覆盖所有关键的外键关系配置

## API认证端点设计模式

### JWT端点设计
- 提供标准化的令牌获取/刷新/验证/黑名单端点
- 使用装饰器为API文档提供响应示例
- 扩展基本视图添加自定义响应格式（如用户信息）
- 集中配置URL路由保持一致性
- 使用统一的命名规范（token_obtain_pair, token_refresh等）

### API文档最佳实践
- 使用swagger_auto_schema装饰器定义响应结构
- 创建专用的文档序列化器（不实现create/update方法）
- 为序列化器字段添加help_text提供说明
- 为视图方法添加清晰的注释和说明
- 统一错误响应格式和状态码

### 用户认证流程
- 登录返回令牌和用户信息
- 登出时将刷新令牌加入黑名单
- 提供专用的密码修改端点
- 实现细粒度的权限控制
- 异常处理保证友好的错误提示

## 中间件实现最佳实践

### JWT认证中间件
- 使用JWTAuthentication类验证令牌有效性
- 处理各种令牌异常情况(InvalidToken, TokenError, AuthenticationFailed)
- 记录认证结果和性能指标，便于监控和调试
- 支持排除不需要认证的URL路径
- 为认证失败提供友好的错误消息和标准化响应
- 在请求对象中保存令牌信息供后续使用
- 通过settings.py配置中间件行为

### 请求日志中间件
- 记录请求详细信息（URL、方法、头部、IP地址等）
- 记录响应状态码和处理时间等性能指标
- 对敏感信息（如认证头和密码）进行脱敏处理
- 支持不同日志级别的配置
- 支持限制日志大小，避免过大日志
- 可配置要排除的URL路径
- 根据状态码自动调整日志级别

### 请求内容处理中间件
- 验证请求内容大小，防止过大请求
- 处理JSON请求内容的解析和验证
- 为响应添加安全相关的HTTP头部
- 提供标准化的API响应格式
- 支持自定义响应头部配置
- 维护API版本信息
- 优雅处理各种错误情况


```
