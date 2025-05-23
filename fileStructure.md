# 项目文件结构

## 目录结构映射

```
a7/                           # 项目根目录
├── .roo/                     # Roo助手规则及配置目录
│   ├── rules/                # 基础规则目录
│   ├── rules-architect/      # 架构相关规则目录
│   ├── rules-ask/            # 查询相关规则目录
│   ├── rules-boomerang/      # Boomerang相关规则目录
│   ├── rules-code/           # 代码生成相关规则目录
│   ├── rules-debug/          # 调试相关规则目录
│   └── rules-test/           # 测试相关规则目录
├── a7/                       # Django项目主目录
│   ├── a7/                   # Django项目配置包
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── asgi.py           # ASGI应用配置
│   │   ├── settings.py       # Django设置文件
│   │   ├── urls.py           # URL路由配置
│   │   └── wsgi.py           # WSGI应用配置
│   ├── apps/                 # Django应用程序目录
│   │   ├── __init__.py       # Python包初始化文件
│   │   └── core/             # 核心应用程序
│   │       ├── __init__.py   # Python包初始化文件
│   │       ├── admin.py      # 核心应用Admin配置
│   │       ├── models.py     # 核心应用模型定义
│   │       ├── middleware/   # 核心应用中间件目录
│   │       │   ├── __init__.py              # 中间件包初始化文件
│   │       │   ├── request_logging_middleware.py  # 请求日志记录中间件
│   │       │   └── request_processor_middleware.py # 请求处理中间件
│   │       ├── tests/        # 核心应用测试目录
│   │       │   ├── __init__.py              # 测试包初始化文件
│   │       │   └── test_middleware.py       # 中间件测试文件
│   │       ├── urls.py       # 核心应用路由配置
│   │       └── views.py      # 核心应用视图
│   ├── users/                # 用户管理应用
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── admin.py          # Django Admin配置
│   │   ├── apps.py           # 应用配置
│   │   ├── middleware/       # 用户中间件目录
│   │   │   ├── __init__.py   # 中间件包初始化文件
│   │   │   └── jwt_auth_middleware.py # JWT认证中间件
│   │   ├── models.py         # 用户和角色模型
│   │   ├── permissions.py    # 自定义权限类
│   │   ├── permission_utils.py # 权限工具函数
│   │   ├── serializers.py    # 序列化器
│   │   ├── signals.py        # 信号处理
│   │   ├── tests/            # 用户应用测试目录
│   │   │   ├── __init__.py   # 测试包初始化文件
│   │   │   ├── test_jwt_middleware.py # JWT中间件测试
│   │   │   └── test_models.py # 用户模型测试
│   │   ├── urls.py           # URL路由配置
│   │   ├── views.py          # API视图
│   │   ├── management/       # 管理命令目录
│   │   │   ├── __init__.py   # Python包初始化文件
│   │   │   └── commands/     # 具体命令目录
│   │   │       ├── __init__.py # Python包初始化文件
│   │   │       ├── init_roles.py # 角色和权限初始化命令
│   │   │       └── sync_roles.py # 角色和权限同步命令
│   │   └── migrations/       # 数据库迁移文件
│   ├── courses/              # 课程管理应用
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── admin.py          # 课程模型的Admin配置
│   │   ├── apps.py           # 课程应用配置
│   │   ├── models.py         # 课程相关模型定义
│   │   ├── serializers.py    # 课程序列化器
│   │   ├── permissions.py    # 课程权限类
│   │   ├── urls.py           # 课程应用URL配置
│   │   ├── views.py          # 课程相关视图和API实现
│   │   ├── validations.py    # 通用验证工具类
│   │   ├── utils.py          # 工具函数，包含请求参数验证
│   │   ├── tests.py          # 课程模型的测试用例
│   │   ├── tests_api.py      # 课程API的测试用例
│   │   ├── tests_validation.py # 验证逻辑的测试用例
│   │   └── migrations/       # 课程模型数据库迁移文件
│   ├── db.sqlite3            # SQLite数据库文件
│   ├── permission.log        # 项目级权限日志文件
│   ├── request.log           # 请求日志文件
│   ├── jwt_auth.log          # JWT认证日志文件
│   └── manage.py             # Django命令行工具
├── scripts/                  # 脚本和工具目录
│   └── example_prd.txt       # 产品需求文档示例
├── tasks/                    # 任务文件目录（Task Master生成的任务）
├── test_html/                # 测试HTML文件目录
│   ├── auth_test.html        # 登录/登出/密码更改功能测试页面
│   └── permissions_test.html # 角色权限测试页面
├── test_api.py               # API测试脚本，用于测试中间件功能
├── .env.example              # 环境变量示例文件
├── .gitignore                # Git忽略配置文件
├── .roomodes                 # Roo模式配置文件
├── .taskmasterconfig         # Task Master配置文件
├── .windsurfrules            # Windsurf规则配置文件
├── a7.code-workspace         # VS Code工作区配置文件
├── fileStructure.md          # 项目文件结构文档（本文件）
├── library.md                # 项目库文档
├── permission.log            # 权限检查日志文件
├── request.log               # 请求日志文件
├── jwt_auth.log              # JWT认证日志文件
└── prd.txt                   # 产品需求文档文件
```

## 文件用途说明

### Django项目文件

- **a7/a7/__init__.py**: Python包标识文件，表明该目录是一个Python包。
- **a7/a7/asgi.py**: ASGI（异步服务器网关接口）应用配置，用于异步服务器部署。
- **a7/a7/settings.py**: Django项目的核心配置文件，包含数据库、应用、中间件等设置。包含完整的Django REST Framework配置，定义了API认证（JWT和会话认证）、权限控制、分页（每页20条）、渲染器（JSON和可视化API）、解析器、异常处理、过滤、版本控制、JSON格式和时间格式等全局设置。
- **a7/a7/urls.py**: URL路由配置，定义请求路径与视图函数的映射关系。
- **a7/a7/wsgi.py**: WSGI（Web服务器网关接口）应用配置，用于传统Web服务器部署。
- **a7/manage.py**: Django命令行工具，用于执行各种管理任务，如运行开发服务器、数据库迁移等。
- **a7/db.sqlite3**: SQLite数据库文件，存储项目的所有数据，包括用户、角色、权限、课程、知识点等实体数据。在开发环境中使用，包含测试和示例数据。
- **a7/permission.log**: 项目级权限检查日志文件，记录权限中间件在a7目录下的日志。

### Django应用文件

- **a7/apps/__init__.py**: Python包标识文件，将apps目录标记为Python包。
- **a7/apps/core/__init__.py**: Core应用的Python包标识文件。
- **a7/apps/core/models.py**: 模型定义，包含UsageStatistics（使用统计）和PerformanceMetric（性能指标）模型，用于记录用户活动和系统性能。
- **a7/apps/core/admin.py**: Django Admin后台配置，定义UsageStatistics和PerformanceMetric模型在管理界面的展示方式和操作功能。
- **a7/apps/core/tests.py**: 测试文件，包含对UsageStatistics和PerformanceMetric模型的全面测试，包括基础功能测试、JSON字段处理测试和真实场景模拟测试。
- **a7/apps/core/urls.py**: Core应用的URL路由配置，定义了API端点路径与视图的映射。
- **a7/apps/core/views.py**: Core应用的视图文件，包含API端点的实现逻辑，如健康检查接口。

### 中间件文件

- **a7/apps/core/middleware/request_logging_middleware.py**: 请求日志中间件，负责记录API请求信息，包括请求方法、路径、状态码和响应时间。支持排除特定路径，避免记录静态文件等不必要的请求。
- **a7/apps/core/middleware/request_processor_middleware.py**: 请求处理中间件，负责验证请求内容、添加安全响应头和限制请求大小。实现了请求大小限制检查、JSON格式验证和API响应标准化。
- **a7/users/middleware/jwt_auth_middleware.py**: JWT认证中间件，负责验证JWT令牌、记录认证过程和处理无效令牌情况。支持自定义错误响应和认证日志记录，提高API安全性。

### 用户管理应用文件

- **a7/users/__init__.py**: Users应用的Python包标识文件。
- **a7/users/admin.py**: Django Admin后台配置，定义用户和角色模型在管理界面的展示方式和操作功能。
- **a7/users/apps.py**: 应用配置文件，包含应用元数据和启动逻辑。
- **a7/users/models.py**: 模型定义，包含扩展的User模型和Role模型，实现基于角色的用户模型和权限系统。
- **a7/users/permissions.py**: 自定义权限类，定义基于角色和功能的权限类，如IsAdmin、IsTeacher、IsAdminOrTeacher等。
- **a7/users/permission_utils.py**: 权限工具函数，提供权限分配、管理和同步功能，实现基于角色的权限自动分配。
- **a7/users/middleware/jwt_auth_middleware.py**: JWT认证中间件，负责验证JWT令牌、记录认证过程和处理无效令牌情况。
- **a7/users/signals.py**: 信号处理器，包含用户创建时自动生成令牌和分配权限的逻辑，以及角色和权限变更的处理。
- **a7/users/tests/test_jwt_middleware.py**: JWT中间件测试文件，包含对JWTAuthMiddleware的单元测试，验证令牌验证、过期令牌处理和认证日志记录功能。
- **a7/users/urls.py**: URL路由配置，定义用户API端点，包括用户管理、角色管理、登录和登出端点。
- **a7/users/views.py**: 视图文件，包含UserViewSet（含权限控制）和RoleViewSet视图集，自定义的认证视图（CustomTokenObtainPairView和装饰类），以及登出视图（LogoutView）。还包括完整的Swagger文档装饰类（DecoratedTokenObtainPairView、DecoratedTokenRefreshView、DecoratedTokenVerifyView、DecoratedTokenBlacklistView）。
- **a7/users/management/commands/init_roles.py**: 管理命令，用于初始化角色和权限，并更新现有用户的权限设置。
- **a7/users/management/commands/sync_roles.py**: 管理命令，用于同步用户角色和权限数据，修复数据不一致问题。

### 课程管理应用文件

- **a7/courses/__init__.py**: Courses应用的Python包标识文件。
- **a7/courses/admin.py**: 课程相关模型的Admin配置，定义Course、KnowledgePoint、Courseware、Exercise、StudentAnswer和LearningRecord模型在管理界面的展示方式和操作功能。
- **a7/courses/apps.py**: 课程应用配置文件，包含应用元数据和中文名称设置。
- **a7/courses/models.py**: 模型定义，包含Course（课程）、KnowledgePoint（知识点）、Courseware（课件）、Exercise（练习题）、StudentAnswer（学生答案）和LearningRecord（学习记录）模型，实现课程内容管理、练习评测系统和学习进度跟踪功能。
- **a7/courses/serializers.py**: 课程序列化器定义，包含CourseSerializer（读取）、CourseCreateSerializer（创建）和CourseUpdateSerializer（更新）类，负责课程数据的序列化与反序列化。还包含KnowledgePointSerializer（读取，含课程标题、父知识点标题和子知识点列表）、KnowledgePointCreateSerializer（创建，含父知识点属于同一课程的验证）和KnowledgePointUpdateSerializer（更新，含循环引用和跨课程引用验证）类，负责知识点数据的序列化与反序列化。实现了验证方法（validate_title、validate_subject等），确保数据有效性和一致性。
- **a7/courses/permissions.py**: 课程权限类定义，包含IsTeacherOrAdmin（教师或管理员权限）和IsCourseTeacherOrAdmin（课程教师或管理员权限）类，负责课程API的权限控制。还包含IsKnowledgePointCourseTeacherOrAdmin权限类，确保只有知识点所属课程的教师或管理员可以修改或删除知识点。
- **a7/courses/urls.py**: 课程应用的URL路由配置，使用DefaultRouter注册CourseViewSet和KnowledgePointViewSet。
- **a7/courses/views.py**: 课程相关的视图文件，包含CourseViewSet视图集，实现课程的CRUD操作和自定义操作(如my_courses)，提供完整的课程API功能。还包含KnowledgePointViewSet视图集，实现知识点的CRUD操作、按课程和父知识点筛选以及自定义操作（如top_level和children），支持层级结构管理和动态序列化器。还实现了请求参数验证，确保API输入数据的有效性。
- **a7/courses/validations.py**: 通用验证工具类，提供了字段验证（validate_text_field）、对象存在性验证（validate_existence）和唯一性验证（validate_uniqueness）等方法，为序列化器提供复用的验证逻辑。
- **a7/courses/utils.py**: 工具函数文件，包含validate_required_params函数，用于验证请求中必需的参数是否存在，支持GET和POST/PUT/PATCH请求，适用于自定义操作和视图方法。
- **a7/courses/tests.py**: 测试文件，包含课程模型的单元测试，验证模型创建、关系和功能正确性，以及练习题、学生答案和学习记录的测试用例。
- **a7/courses/tests_api.py**: 课程API测试文件，包含API接口的功能测试，验证权限控制、CRUD操作和自定义操作的正确性，包括KnowledgePointAPITests测试类，验证知识点API的功能完整性和权限控制。
- **a7/courses/tests_validation.py**: 验证逻辑测试文件，包含对课程、知识点和课件API的验证逻辑测试，验证字段验证、唯一性检查、关系完整性（如循环引用检测）等验证功能的正确性。测试不同场景下的验证行为，确保数据一致性和业务规则的强制执行。
- **a7/courses/migrations/**: 包含课程模型的数据库迁移文件，记录模型结构的变更历史。

### 测试文件

- **test_html/auth_test.html**: 用于测试登录/登出/密码更改功能的HTML页面，提供基本UI和JavaScript测试代码，通过浏览器直接测试认证API。
- **test_html/permissions_test.html**: 角色权限测试页面，用于测试不同角色用户的权限访问控制，支持多角色登录和API权限验证。
- **a7/users/tests.py**: 包含完整的自动化测试套件，测试认证功能（登录、登出、密码更改）、基于角色的权限控制以及完整的用户流程端到端测试。
- **a7/courses/tests.py**: 包含课程模型的自动化测试，验证课程内容管理功能的正确性，以及练习题、学生答案和学习记录的功能测试，包括学习进度跟踪、状态转换和统计分析测试。
- **a7/apps/core/tests.py**: 包含核心模型的自动化测试，验证用户活动跟踪和系统性能监控功能，测试JSON字段处理方法和真实应用场景模拟。
- **a7/apps/core/tests/test_middleware.py**: 核心中间件测试文件，包含对RequestLoggingMiddleware和RequestProcessorMiddleware的单元测试，验证路径排除、日志记录、请求验证、响应处理和请求大小限制功能。
- **test_api.py**: API测试脚本，用于集成测试中间件功能，包括JWT认证、请求日志和请求处理。提供实际HTTP请求测试，验证中间件在真实环境中的表现。

### 配置文件

- **.taskmasterconfig**: Task Master工具的配置文件，定义AI模型设置和全局配置参数。
- **.gitignore**: 指定Git版本控制系统应忽略的文件模式。
- **.roomodes**: Roo助手的模式配置，定义Roo的行为模式。
- **.windsurfrules**: Windsurf工具的规则配置。
- **a7.code-workspace**: VS Code工作区配置，定义项目在VS Code中的显示和行为。
- **.env.example**: 环境变量示例模板，用于配置各种API密钥和环境特定设置。
- **permission.log**: 权限检查日志文件，记录权限中间件的访问尝试和拒绝信息。
- **request.log**: 请求日志文件，由RequestLoggingMiddleware生成，记录API请求详情，包括方法、路径、状态码和响应时间。
- **jwt_auth.log**: JWT认证日志文件，由JWTAuthMiddleware生成，记录令牌认证结果，包括成功认证和失败尝试。

### 目录

- **.roo/**: 包含所有Roo助手使用的规则文件，分为多个特定类别，支持不同的功能。
  - **rules/**: 基础通用规则。
  - **rules-architect/**: 系统架构设计相关规则。
  - **rules-ask/**: 询问和交互相关规则。
  - **rules-boomerang/**: Boomerang功能相关规则。
  - **rules-code/**: 代码生成和编写相关规则。
  - **rules-debug/**: 调试和错误处理相关规则。
  - **rules-test/**: 测试和质量保证相关规则。
  
- **.cursor/**: Cursor IDE的配置和扩展设置，包括MCP（Model Control Protocol）配置、环境变量设置和编辑器特定功能规则。用于增强IDE与项目的集成，提供自定义命令和工具支持。

- **scripts/**: 包含各种实用工具脚本和配置模板。
  - **example_prd.txt**: 产品需求文档(PRD)的示例模板，用于Task Master解析并生成任务。

- **a7/apps/**: Django应用程序目录，包含项目中的各个应用模块。
  - **core/**: 核心应用模块，实现基础API功能，如健康检查接口。

- **a7/users/**: 用户管理应用，实现用户认证与授权系统。

- **a7/courses/**: 课程管理应用，实现课程内容管理和课程资源组织功能。

- **tasks/**: 由Task Master生成和管理的任务文件目录，包含项目任务的结构化描述。

- **test_html/**: 包含测试文件，用于前端测试特定功能，如认证和权限控制。

### 文档文件

- **fileStructure.md**: 本文档，提供项目文件和目录的完整映射及其用途。
- **library.md**: 项目使用的库、框架和工具的文档。
- **prd.txt**: 产品需求文档(PRD)，描述项目功能、技术架构、开发路线图和系统需求，用于Task Master生成任务。

## 关键文件之间的关系

1. **Django项目结构**:
   - `a7/a7/settings.py`定义Django项目的核心配置，如数据库连接、安装的应用等。
   - `a7/a7/settings.py`中的`REST_FRAMEWORK`字典配置REST API框架的全局行为，包括认证、权限、分页、渲染器、解析器、过滤和版本控制等，为所有API端点提供一致的基础设置。
   - `a7/a7/urls.py`配置URL路由，将请求映射到对应的视图函数。
   - `a7/a7/asgi.py`和`a7/a7/wsgi.py`提供异步和同步Web服务器网关接口。
   - `a7/manage.py`是命令行工具入口，用于执行Django管理命令。
   - `a7/apps/core/urls.py`定义核心应用的URL路径，被主urls.py文件包含。
   - `a7/apps/core/views.py`实现API端点的视图逻辑，如健康检查接口。

2. **用户认证与授权系统**:
   - `a7/users/models.py`定义自定义User模型和Role模型，是系统权限设计的基础，实现基于角色的用户模型和权限系统。
   - `a7/users/permissions.py`实现细粒度的权限控制系统，包含多种基于角色和功能的权限类。
   - `a7/users/permission_utils.py`提供权限工具函数，实现权限的自动分配、管理和同步。
   - `a7/users/middleware/jwt_auth_middleware.py`实现JWT认证中间件，提供令牌验证、认证日志记录和自定义错误响应，是整个认证系统的关键环节。
   - `a7/users/signals.py`处理用户创建、角色变更和权限同步的信号，确保权限系统的一致性。
   - `a7/users/management/commands/init_roles.py`提供管理命令初始化角色和权限数据。
   - `a7/users/management/commands/sync_roles.py`提供管理命令同步用户角色和权限数据，修复数据不一致问题。
   - `a7/users/serializers.py`实现数据转换，支持REST API的用户数据处理，包含密码更改的验证逻辑以及各种令牌响应的序列化器（为Swagger/ReDoc文档提供示例）。
   - `a7/users/views.py`提供用户和角色管理的API端点，以及登录/登出/密码更改功能，并使用权限类控制访问。该文件还包括增强的JWT令牌视图实现，通过装饰器模式为Swagger文档提供标准化响应，以及令牌验证和黑名单功能。
   - `a7/users/urls.py`定义用户API路由，被主urls.py包含，负责将请求路由到对应的视图函数。
   - `a7/a7/urls.py`定义顶级URL路由，集成JWT认证端点(`/api/token/`, `/api/token/refresh/`, `/api/token/verify/`, `/api/token/blacklist/`)以及各应用的URL配置。
   - `a7/a7/settings.py`中的`AUTH_USER_MODEL`设置指向自定义User模型，还包含MIDDLEWARE配置中的权限中间件和日志配置。
   - `a7/a7/settings.py`中的`SIMPLE_JWT`配置定义JWT令牌的行为，包括黑名单和令牌轮换设置。
   - `a7/a7/settings.py`中的`REST_FRAMEWORK`配置与JWT认证和权限系统集成，通过`DEFAULT_AUTHENTICATION_CLASSES`和`DEFAULT_PERMISSION_CLASSES`确保API端点的安全访问。
   - `a7/users/tests.py`提供认证和权限功能的自动化测试，确保系统按预期工作。
   - `test_html/auth_test.html`和`test_html/permissions_test.html`提供基于浏览器的手动测试界面，验证API交互。
   - `permission.log`记录权限中间件的访问检查日志，帮助调试和监控权限系统。

3. **课程内容管理系统**:
   - `a7/courses/models.py`定义Course、KnowledgePoint、Courseware、Exercise、StudentAnswer和LearningRecord模型，实现课程内容的组织和管理以及练习评测功能。
   - `a7/courses/admin.py`配置课程相关模型在Django Admin中的展示和操作方式。
   - `a7/courses/tests.py`提供课程模型的自动化测试，验证其功能正确性，以及练习题、学生答案和学习记录的功能测试。
   - `a7/courses/serializers.py`定义序列化器，将课程和知识点模型转换为JSON格式以支持API接口，包括课程相关的序列化器实现自动设置当前用户为教师，知识点序列化器实现层级结构的展示和验证（包括防止循环引用和跨课程引用）。
   - `a7/courses/permissions.py`定义权限类，实现基于角色和所有权的访问控制，确保只有教师和管理员可以创建课程和知识点，只有课程/知识点创建者和管理员可以修改或删除它们。
   - `a7/courses/views.py`实现CourseViewSet和KnowledgePointViewSet视图集，提供完整的CRUD API功能和自定义接口(如my_courses, top_level, children)，使用权限类控制访问，根据不同操作类型动态选择序列化器，支持丰富的筛选功能。
   - `a7/courses/validations.py`提供重用的验证逻辑，如字段验证、对象存在性验证和唯一性验证，为序列化器提供标准化的验证方法，确保API输入数据有效性。
   - `a7/courses/utils.py`包含请求参数验证函数，用于验证必需参数是否存在，确保API收到所需的输入数据，提高API健壮性和用户体验。
   - `a7/courses/tests_validation.py`提供对验证逻辑的专门测试，验证字段验证、唯一性检查、关系完整性验证等功能的正确性，确保数据一致性和业务规则的强制执行。
   - `a7/courses/urls.py`将课程应用的URL配置集成到主URL配置中，启用API路由。
   - `a7/a7/urls.py`将课程应用的URL配置集成到主URL配置中，启用API路由。
   - `a7/a7/settings.py`中的`REST_FRAMEWORK`配置提供API基础设置，包括认证、分页、搜索和过滤功能，被课程和知识点API继承和使用。
   - `a7/apps/core/middleware/request_processor_middleware.py`将API响应标准化为统一格式，包装原始响应数据，为所有API（包括课程和知识点API）提供一致的响应结构。
   - Course模型与User模型（教师）建立外键关系，表示课程的创建者，采用SET_NULL策略避免删除教师时连带删除课程。
   - Courseware模型与Course和User模型建立外键关系，表示课件所属课程和创建者。Course关系使用CASCADE确保删除课程时级联删除课件，而User关系使用SET_NULL保护课件数据。
   - KnowledgePoint模型通过外键关联Course模型，表示知识点所属的课程，使用CASCADE级联删除。KnowledgePoint模型还可以自关联（parent字段），实现知识点的层级结构，通过序列化器中的验证防止循环引用和跨课程引用。
   - Exercise模型通过外键关联KnowledgePoint模型，表示练习题所属的知识点，使用CASCADE级联删除。
   - StudentAnswer模型通过外键关联Exercise模型和User模型，表示学生对特定练习题的回答，均使用CASCADE级联删除。
   - StudentAnswer模型使用unique_together约束确保每个学生对每道题目只能有一个答案。
   - 所有模型均添加了优化索引，提高查询性能，如course_subj_grade_idx索引(Course模型)，kp_course_imp_idx索引(KnowledgePoint模型)等。
   - `a7/courses/tests.py`中的ComprehensiveModelRelationshipTest测试类验证所有模型关系、外键、反向查询和级联删除行为，包括教师删除对课程的影响、课程删除对知识点的级联删除等。

4. **Task Master相关**:
   - `.taskmasterconfig`定义Task Master的行为和使用的AI模型。
   - `scripts/example_prd.txt`提供用于生成任务的PRD模板。
   - `prd.txt`是基于示例创建的实际产品需求文档，用于任务生成。
   - `tasks/`目录存储由Task Master基于PRD生成的任务文件。

5. **测试相关**:
   - `test_html/auth_test.html`提供基于浏览器的认证测试界面，用于验证登录/登出/密码更改功能。
   - `test_html/permissions_test.html`提供角色权限测试界面，用于验证不同角色用户的权限控制和API访问限制。
   - `a7/users/tests.py`包含自动化单元测试，覆盖认证、权限和端到端用户场景测试。
   - `a7/courses/tests.py`包含课程模型的全面自动化测试，包括: 1) ComprehensiveModelRelationshipTest（测试所有模型关系和级联行为）；2) ModelFieldUpdateTest（测试字段更新和业务逻辑验证）；3) EdgeCaseAndSpecialConditionTest（测试边界条件和特殊情况）；4) AdvancedQueryTest（测试Q对象、F表达式、Case When表达式和复杂聚合查询）。通过81个完整测试用例全面验证模型功能的正确性和健壮性。

6. **Roo助手规则**:
   - `.roomodes`定义Roo助手的行为模式。
   - `.roo/`下的各个子目录包含不同类别的规则，共同支持Roo助手的功能。
   - `.windsurfrules`配合Roo规则，定义项目的代码和文档生成规则。

7. **开发环境配置**:
   - `a7.code-workspace`定义VS Code的项目视图和配置。
   - `.cursor/`包含Cursor IDE的特定配置。
   - `.env.example`提供需要的环境变量配置模板。

8. **用户活动和性能监控系统**:
   - `a7/apps/core/models.py`定义UsageStatistics和PerformanceMetric模型，用于跟踪用户活动和系统性能。
   - `a7/apps/core/admin.py`配置这些模型在Django Admin中的展示和操作方式。
   - `a7/apps/core/tests.py`提供这些模型的自动化测试，验证其功能正确性。
   - UsageStatistics模型与User模型建立外键关系，跟踪特定用户的系统使用情况。
   - UsageStatistics和PerformanceMetric模型都使用JSON字段存储复杂的详细信息，并提供解析方法。

9. **学习进度跟踪系统**:
   - `a7/courses/models.py`中的LearningRecord模型用于跟踪学生的学习进度和时间投入。
   - LearningRecord模型通过外键关联User(student)、Course和KnowledgePoint模型，建立学生-课程-知识点的学习关系，使用CASCADE级联删除。
   - LearningRecord模型提供进度更新方法、时间累计方法和状态判断属性，实现完整的学习进度跟踪功能。
   - `a7/courses/admin.py`配置LearningRecord模型在Django Admin中的展示和操作方式。
   - `a7/courses/tests.py`提供学习记录模型的自动化测试，验证学习进度跟踪、状态转换和统计分析功能。
   - LearningRecord模型添加了lr_progress_idx等多个优化索引，提高查询性能。

10. **模型关系优化系统**:
    - 为所有模型添加了优化的索引设计，提高查询性能。
    - 实现了精心设计的外键关系级联删除策略：用户相关使用SET_NULL保护数据，内容关系使用CASCADE维持一致性。
    - 所有索引和外键关系均在迁移文件中正确定义，如`a7/courses/migrations/0004_rename_courses_lea_student_a74868_idx_lr_stud_course_idx_and_more.py`。
    - `a7/courses/tests.py`中的ComprehensiveModelRelationshipTest测试类验证所有级联删除行为和唯一性约束。ModelFieldUpdateTest测试类验证字段更新和业务逻辑，EdgeCaseAndSpecialConditionTest测试类验证边界条件和特殊情况，AdvancedQueryTest测试类验证高级查询功能。
    - UsageStatistics模型采用SET_NULL策略连接User模型，避免删除用户时丢失重要的使用统计数据。
    - 所有模型的索引都有明确的命名约定，如lr_stud_course_idx、ans_ex_score_idx等，便于维护和调试。
    - `a7/a7/settings.py`中的DRF分页、过滤和搜索配置与模型查询优化协同工作，确保API响应高效且符合最佳实践。

11. **REST Framework API系统**:
    - `a7/a7/settings.py`中的`REST_FRAMEWORK`配置定义全局API行为和标准。
    - DRF配置与用户认证系统无缝集成，提供JWT令牌和会话认证支持。
    - `a7/users/middleware/jwt_auth_middleware.py`与DRF认证类协同工作，实现无缝的令牌验证和用户身份识别。
    - `a7/apps/core/middleware/request_processor_middleware.py`确保API响应格式标准化，添加安全响应头，提高API交互的一致性和安全性。
    - `a7/apps/core/middleware/request_logging_middleware.py`记录API调用信息，为性能优化和问题诊断提供数据支持。
    - 分页配置确保大型数据集的高效处理，防止返回过多数据导致性能问题。
    - 渲染器配置支持多种格式输出，既可返回生产环境的JSON数据，也支持开发环境的可视化API界面。
    - 解析器配置支持多种输入格式，包括JSON数据、表单数据和文件上传。
    - 过滤和搜索配置为API提供强大的数据查询能力，支持高级搜索和结果排序。
    - 异常处理确保API错误以一致的格式返回，便于客户端处理。
    - 版本控制配置支持API演进和向后兼容性管理。
    - 格式配置优化响应大小和时间表示，提高API效率和可用性。
    - 测试配置简化API自动化测试开发。

12. **API监控与日志系统**:
    - `a7/apps/core/middleware/request_logging_middleware.py`实现API请求监控，记录请求方法、路径、状态码和处理时间。
    - `a7/users/middleware/jwt_auth_middleware.py`记录认证过程，包括成功认证和失败尝试。
    - `request.log`存储API请求日志，提供系统调用情况的完整记录。
    - `jwt_auth.log`存储认证日志，记录用户认证活动，有助于安全审计和问题排查。
    - `a7/a7/settings.py`中的`LOGGING`配置定义了日志记录的格式、级别和目标，实现灵活的日志管理。
    - `REQUEST_LOG_EXCLUDE_PATHS`和`PROCESSOR_EXCLUDE_PATHS`配置排除某些路径，避免记录不必要的请求，提高系统效率。
    - `a7/apps/core/tests/test_middleware.py`验证日志记录功能的正确性和完整性。
    - 日志系统与性能监控系统(`PerformanceMetric`模型)协同工作，提供系统运行情况的全面视图。

## 目录组织逻辑

项目采用了以下组织逻辑：

1. **Django项目结构**:
   - 遵循Django标准项目结构，核心配置放在内部a7包中。
   - Django应用存放在apps目录下，如core应用。
   - 用户管理系统作为独立应用(users)实现，便于模块化管理。
   - 课程管理系统作为独立应用(courses)实现，集中管理课程相关功能。
   - 每个应用都有自己的URLs和视图模块。

2. **按工具分类**: 
   - 每个主要工具(Task Master, Roo, Cursor)都有其专用配置文件和目录。

3. **按功能分类**:
   - `.roo/`中的规则按功能领域划分到不同子目录。
   - `scripts/`目录用于存放工具脚本和模板。
   - `tasks/`专门用于任务管理。
   - `apps/`、`users/`和`courses/`目录按功能划分不同的Django应用。
   - `test_html/`目录包含前端测试文件，按功能分类。

4. **配置与内容分离**:
   - 配置文件(如`.taskmasterconfig`, `.roomodes`)位于根目录。
   - 实际内容(如规则文件、任务文件)存储在相关子目录中。

5. **测试与实现分离**:
   - 单元测试放在应用目录中(`users/tests.py`, `courses/tests.py`)
   - 手动/前端测试文件放在单独的`test_html/`目录下
   - 日志文件`permission.log`放在根目录，便于快速访问和检查

## 命名约定

1. **目录命名**:
   - 以功能或工具名称作为前缀，如`rules-architect/`表示架构相关规则。
   - 使用小写字母和连字符(-)分隔单词，如`rules-debug/`。
   - Django应用目录使用全小写字母，单数形式命名，如`core/`、`users/`、`courses/`。

2. **配置文件命名**:
   - 以点(.)开头的隐藏文件用于配置，如`.taskmasterconfig`。
   - 采用全小写字母，使用描述性名称。

3. **文档文件命名**:
   - 使用驼峰式(CamelCase)或以单词首字母大写，如`fileStructure.md`。
   - 使用描述性名称，清晰表达文件内容。

4. **代码约定**:
   - 代码文件（当添加时）将遵循各语言的标准命名约定。
   - 组件和模块文件名应反映其功能和类型。
   - Django模型类使用单数名词，首字母大写的驼峰式命名(如`User`、`Role`、`Course`、`KnowledgePoint`、`Exercise`、`StudentAnswer`)。
   - Django视图函数使用小写下划线命名(如`user_login`)。
   - Django URL路径使用小写和连字符分隔(如`user-profile/`)。

## API结构

项目已配置以下API结构：

1. **REST Framework全局配置**:
   - **认证配置**: 使用JWT令牌认证和会话认证（支持API浏览器）
   - **权限配置**: 默认要求用户身份验证
   - **分页配置**: 使用页码分页，默认每页20条数据
   - **渲染器配置**: 支持JSON和可浏览API格式输出
   - **解析器配置**: 支持JSON、表单数据和多部分表单数据（含文件上传）输入
   - **异常处理**: 使用默认异常处理器处理API错误
   - **过滤配置**: 支持搜索过滤和结果排序
   - **版本控制**: 使用URL命名空间进行API版本控制
   - **格式配置**: 启用压缩JSON减少响应大小，自定义日期时间格式
   - **测试配置**: 测试客户端默认使用JSON格式

2. **认证端点**:
   - `/api/token/` - 获取JWT认证令牌（DecoratedTokenObtainPairView），返回用户信息和访问/刷新令牌
   - `/api/token/refresh/` - 刷新JWT令牌（DecoratedTokenRefreshView）
   - `/api/token/verify/` - 验证JWT令牌的有效性（DecoratedTokenVerifyView）
   - `/api/token/blacklist/` - JWT令牌黑名单端点（DecoratedTokenBlacklistView），使令牌失效
   - `/api/login/` - 自定义登录端点，返回JWT令牌和用户信息
   - `/api/logout/` - 登出端点，将刷新令牌加入黑名单使其失效

3. **用户管理API**:
   - `/api/users/` - 用户列表和创建
   - `/api/users/<id>/` - 用户详情、更新和删除
   - `/api/users/me/` - 获取当前登录用户信息
   - `/api/users/change_password/` - 修改当前用户密码
   - `/api/users/my_permissions/` - 获取当前用户的权限信息
   - `/api/roles/` - 角色列表和创建
   - `/api/roles/<id>/` - 角色详情、更新和删除
   - `/api/roles/<id>/permissions/` - 获取特定角色的权限信息

4. **核心API**:
   - `/api/health/` - 健康检查端点，提供API服务状态

5. **文档端点**:
   - `/swagger/` - Swagger UI API交互式文档
   - `/redoc/` - ReDoc 格式的API文档

6. **课程管理API**:
   - `/api/courses/` - 课程列表和创建（支持分页、搜索和排序）
   - `/api/courses/<id>/` - 课程详情、更新和删除
   - `/api/courses/my_courses/` - 获取当前登录教师创建的课程列表
   - `/api/knowledge-points/` - 知识点列表和创建（支持按课程和父知识点筛选）
   - `/api/knowledge-points/<id>/` - 知识点详情、更新和删除
   - `/api/knowledge-points/top_level/` - 获取顶级知识点（没有父级的知识点，支持按课程筛选）
   - `/api/knowledge-points/<id>/children/` - 获取特定知识点的子知识点列表（按重要性降序排序）
   - `/api/courseware/` - 课件列表和创建（支持分页、搜索和按课程筛选）
   - `/api/courseware/<id>/` - 课件详情、更新和删除
   - `/api/courseware/by_course/` - 获取指定课程的所有课件
   - 所有端点实现权限控制，确保只有教师和管理员可以创建课程和知识点，只有课程/知识点创建者和管理员可以修改或删除
   - 所有端点包含全面的验证逻辑，确保数据一致性、有效性和适当的错误处理
   - 所有端点返回标准化的响应格式，包含状态码、成功标志和数据

## 练习与评测系统

新增的Exercise和StudentAnswer模型为系统提供以下功能支持：

1. **练习题管理**:
   - 支持多种题型：单选题、多选题、填空题、简答题、编程题等
   - 可设置难度等级（1-5级）
   - 与知识点关联，实现按知识点组织练习题
   - 支持答案模板，用于标准答案或选项设置

2. **学生答案管理**:
   - 记录学生提交的答案内容
   - 支持评分和反馈记录
   - 确保每个学生对每道题只有一个有效答案
   - 记录提交时间，支持时间排序

3. **待实现功能**:
   - 练习题推荐API（基于学习进度）
   - 答案自动评测逻辑
   - 学习记录和统计分析

## 数据监控和分析系统

新增的UsageStatistics、PerformanceMetric和LearningRecord模型为系统提供以下功能支持：

1. **用户活动跟踪**:
   - 记录用户在系统中的各类操作（模块、动作、详情）
   - 捕获用户环境信息（IP地址、用户代理）
   - 支持通过JSON字段存储详细操作日志
   - 提供时间轴分析和用户行为模式识别基础

2. **系统性能监控**:
   - 记录多种性能指标类型（响应时间、CPU使用率、内存使用率等）
   - 支持与特定实体（API、服务器）关联
   - 通过JSON字段存储丰富的上下文信息
   - 为性能优化和问题诊断提供数据支持

3. **学习进度跟踪**:
   - 记录学生在特定课程和知识点上的学习状态和进度
   - 跟踪学习时间投入，支持时间统计分析
   - 提供进度更新和时间累计方法
   - 支持学习完成状态判断和进度统计
   - 为学习推荐和个性化学习提供数据基础

## 管理和更新

此文件结构反映了项目的当前状态。随着项目的发展，将添加新的文件和目录，现有的可能会修改。建议定期更新本文档以保持其准确性。

当添加新的重要文件或目录时，请同时更新此文档中的映射、说明和关系部分。 