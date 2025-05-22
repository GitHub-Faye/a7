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


```
