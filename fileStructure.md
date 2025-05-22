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
│   │       ├── urls.py       # 核心应用路由配置
│   │       └── views.py      # 核心应用视图
│   ├── users/                # 用户管理应用
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── admin.py          # Django Admin配置
│   │   ├── apps.py           # 应用配置
│   │   ├── middleware.py     # 基于角色的权限中间件
│   │   ├── models.py         # 用户和角色模型
│   │   ├── permissions.py    # 自定义权限类
│   │   ├── permission_utils.py # 权限工具函数
│   │   ├── serializers.py    # 序列化器
│   │   ├── signals.py        # 信号处理
│   │   ├── tests.py          # 测试文件，包含认证和权限的单元测试
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
│   │   ├── tests.py          # 课程模型的测试用例
│   │   └── migrations/       # 课程模型数据库迁移文件
│   └── manage.py             # Django命令行工具
├── scripts/                  # 脚本和工具目录
│   └── example_prd.txt       # 产品需求文档示例
├── tasks/                    # 任务文件目录（Task Master生成的任务）
├── test_html/                # 测试HTML文件目录
│   ├── auth_test.html        # 登录/登出/密码更改功能测试页面
│   └── permissions_test.html # 角色权限测试页面
├── .env.example              # 环境变量示例文件
├── .gitignore                # Git忽略配置文件
├── .roomodes                 # Roo模式配置文件
├── .taskmasterconfig         # Task Master配置文件
├── .windsurfrules            # Windsurf规则配置文件
├── a7.code-workspace         # VS Code工作区配置文件
├── fileStructure.md          # 项目文件结构文档（本文件）
├── library.md                # 项目库文档
├── permission.log            # 权限检查日志文件
└── prd.txt                   # 产品需求文档文件
```

## 文件用途说明

### Django项目文件

- **a7/a7/__init__.py**: Python包标识文件，表明该目录是一个Python包。
- **a7/a7/asgi.py**: ASGI（异步服务器网关接口）应用配置，用于异步服务器部署。
- **a7/a7/settings.py**: Django项目的核心配置文件，包含数据库、应用、中间件等设置。
- **a7/a7/urls.py**: URL路由配置，定义请求路径与视图函数的映射关系。
- **a7/a7/wsgi.py**: WSGI（Web服务器网关接口）应用配置，用于传统Web服务器部署。
- **a7/manage.py**: Django命令行工具，用于执行各种管理任务，如运行开发服务器、数据库迁移等。

### Django应用文件

- **a7/apps/__init__.py**: Python包标识文件，将apps目录标记为Python包。
- **a7/apps/core/__init__.py**: Core应用的Python包标识文件。
- **a7/apps/core/urls.py**: Core应用的URL路由配置，定义了API端点路径与视图的映射。
- **a7/apps/core/views.py**: Core应用的视图文件，包含API端点的实现逻辑，如健康检查接口。

### 用户管理应用文件

- **a7/users/__init__.py**: Users应用的Python包标识文件。
- **a7/users/admin.py**: Django Admin后台配置，定义用户和角色模型在管理界面的展示方式和操作功能。
- **a7/users/apps.py**: 应用配置文件，包含应用元数据和启动逻辑。
- **a7/users/models.py**: 模型定义，包含扩展的User模型和Role模型，实现基于角色的用户模型和权限系统。
- **a7/users/permissions.py**: 自定义权限类，定义基于角色和功能的权限类，如IsAdmin、IsTeacher、IsAdminOrTeacher等。
- **a7/users/permission_utils.py**: 权限工具函数，提供权限分配、管理和同步功能，实现基于角色的权限自动分配。
- **a7/users/middleware.py**: 基于角色的权限中间件，实现权限检查日志记录和自定义权限拒绝响应。
- **a7/users/serializers.py**: 序列化器类，处理用户和角色数据的序列化和反序列化，以及密码更改验证。
- **a7/users/signals.py**: 信号处理器，包含用户创建时自动生成令牌和分配权限的逻辑，以及角色和权限变更的处理。
- **a7/users/tests.py**: 测试文件，包含用户认证系统和角色权限的全面单元测试，验证登录、登出、密码更改和基于角色的权限控制功能。
- **a7/users/urls.py**: URL路由配置，定义用户API端点。
- **a7/users/views.py**: 视图文件，包含UserViewSet（含权限控制）和RoleViewSet视图集及登录/登出视图的实现。
- **a7/users/management/commands/init_roles.py**: 管理命令，用于初始化角色和权限，并更新现有用户的权限设置。
- **a7/users/management/commands/sync_roles.py**: 管理命令，用于同步用户角色和权限数据，修复数据不一致问题。

### 课程管理应用文件

- **a7/courses/__init__.py**: Courses应用的Python包标识文件。
- **a7/courses/admin.py**: 课程相关模型的Admin配置，定义Course、KnowledgePoint、Courseware、Exercise和StudentAnswer模型在管理界面的展示方式和操作功能。
- **a7/courses/apps.py**: 课程应用配置文件，包含应用元数据和中文名称设置。
- **a7/courses/models.py**: 模型定义，包含Course（课程）、KnowledgePoint（知识点）、Courseware（课件）、Exercise（练习题）和StudentAnswer（学生答案）模型，实现课程内容管理和练习评测系统。
- **a7/courses/tests.py**: 测试文件，包含课程模型的单元测试，验证模型创建、关系和功能正确性，以及练习题和学生答案的测试用例。
- **a7/courses/migrations/**: 包含课程模型的数据库迁移文件，记录模型结构的变更历史。

### 测试文件

- **test_html/auth_test.html**: 用于测试登录/登出/密码更改功能的HTML页面，提供基本UI和JavaScript测试代码，通过浏览器直接测试认证API。
- **test_html/permissions_test.html**: 角色权限测试页面，用于测试不同角色用户的权限访问控制，支持多角色登录和API权限验证。
- **a7/users/tests.py**: 包含完整的自动化测试套件，测试认证功能（登录、登出、密码更改）、基于角色的权限控制以及完整的用户流程端到端测试。
- **a7/courses/tests.py**: 包含课程模型的自动化测试，验证课程内容管理功能的正确性，以及练习题和学生答案的功能测试，包括约束和关系测试。

### 配置文件

- **.taskmasterconfig**: Task Master工具的配置文件，定义AI模型设置和全局配置参数。
- **.gitignore**: 指定Git版本控制系统应忽略的文件模式。
- **.roomodes**: Roo助手的模式配置，定义Roo的行为模式。
- **.windsurfrules**: Windsurf工具的规则配置。
- **a7.code-workspace**: VS Code工作区配置，定义项目在VS Code中的显示和行为。
- **.env.example**: 环境变量示例模板，用于配置各种API密钥和环境特定设置。
- **permission.log**: 权限检查日志文件，记录权限中间件的访问尝试和拒绝信息。

### 目录

- **.roo/**: 包含所有Roo助手使用的规则文件，分为多个特定类别，支持不同的功能。
  - **rules/**: 基础通用规则。
  - **rules-architect/**: 系统架构设计相关规则。
  - **rules-ask/**: 询问和交互相关规则。
  - **rules-boomerang/**: Boomerang功能相关规则。
  - **rules-code/**: 代码生成和编写相关规则。
  - **rules-debug/**: 调试和错误处理相关规则。
  - **rules-test/**: 测试和质量保证相关规则。
  
- **.cursor/**: Cursor IDE的配置和扩展设置，包括特定于编辑器的功能规则。

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
   - `a7/a7/urls.py`配置URL路由，将请求映射到对应的视图函数。
   - `a7/a7/asgi.py`和`a7/a7/wsgi.py`提供异步和同步Web服务器网关接口。
   - `a7/manage.py`是命令行工具入口，用于执行Django管理命令。
   - `a7/apps/core/urls.py`定义核心应用的URL路径，被主urls.py文件包含。
   - `a7/apps/core/views.py`实现API端点的视图逻辑，如健康检查接口。

2. **用户认证与授权系统**:
   - `a7/users/models.py`定义自定义User模型和Role模型，是系统权限设计的基础，实现基于角色的用户模型和权限系统。
   - `a7/users/permissions.py`实现细粒度的权限控制系统，包含多种基于角色和功能的权限类。
   - `a7/users/permission_utils.py`提供权限工具函数，实现权限的自动分配、管理和同步。
   - `a7/users/middleware.py`实现权限中间件，提供权限检查日志和自定义响应。
   - `a7/users/signals.py`处理用户创建、角色变更和权限同步的信号，确保权限系统的一致性。
   - `a7/users/management/commands/init_roles.py`提供管理命令初始化角色和权限数据。
   - `a7/users/management/commands/sync_roles.py`提供管理命令同步用户角色和权限数据，修复数据不一致问题。
   - `a7/users/serializers.py`实现数据转换，支持REST API的用户数据处理，包含密码更改的验证逻辑。
   - `a7/users/views.py`提供用户和角色管理的API端点，以及登录/登出/密码更改功能，并使用权限类控制访问。
   - `a7/users/urls.py`定义用户API路由，被主urls.py包含。
   - `a7/a7/settings.py`中的`AUTH_USER_MODEL`设置指向自定义User模型，还包含MIDDLEWARE配置中的权限中间件和日志配置。
   - `a7/a7/settings.py`中的`SIMPLE_JWT`配置定义JWT令牌的行为，包括黑名单和令牌轮换设置。
   - `a7/users/tests.py`提供认证和权限功能的自动化测试，确保系统按预期工作。
   - `test_html/auth_test.html`和`test_html/permissions_test.html`提供基于浏览器的手动测试界面，验证API交互。
   - `permission.log`记录权限中间件的访问检查日志，帮助调试和监控权限系统。

3. **课程内容管理系统**:
   - `a7/courses/models.py`定义Course、KnowledgePoint、Courseware、Exercise和StudentAnswer模型，实现课程内容的组织和管理以及练习评测功能。
   - `a7/courses/admin.py`配置课程相关模型在Django Admin中的展示和操作方式。
   - `a7/courses/tests.py`提供课程模型的自动化测试，验证其功能正确性，以及练习题和学生答案的功能测试。
   - `a7/courses/models.py`中的KnowledgePoint模型使用自引用外键实现知识点的层次结构。
   - Course模型与User模型（教师）建立外键关系，表示课程的创建者。
   - Courseware模型与Course和User模型建立外键关系，表示课件所属课程和创建者。
   - KnowledgePoint模型通过外键关联Course模型，表示知识点所属的课程。
   - Exercise模型通过外键关联KnowledgePoint模型，表示练习题所属的知识点。
   - StudentAnswer模型通过外键关联Exercise模型和User模型，表示学生对特定练习题的回答。
   - StudentAnswer模型使用unique_together约束确保每个学生对每道题目只能有一个答案。

4. **Task Master相关**:
   - `.taskmasterconfig`定义Task Master的行为和使用的AI模型。
   - `scripts/example_prd.txt`提供用于生成任务的PRD模板。
   - `prd.txt`是基于示例创建的实际产品需求文档，用于任务生成。
   - `tasks/`目录存储由Task Master基于PRD生成的任务文件。

5. **测试相关**:
   - `test_html/auth_test.html`提供基于浏览器的认证测试界面，用于验证登录/登出/密码更改功能。
   - `test_html/permissions_test.html`提供角色权限测试界面，用于验证不同角色用户的权限控制和API访问限制。
   - `a7/users/tests.py`包含自动化单元测试，覆盖认证、权限和端到端用户场景测试。
   - `a7/courses/tests.py`包含课程模型的自动化测试，验证课程内容管理功能的正确性，以及练习题和学生答案的功能测试，包括约束和关系测试。

6. **Roo助手规则**:
   - `.roomodes`定义Roo助手的行为模式。
   - `.roo/`下的各个子目录包含不同类别的规则，共同支持Roo助手的功能。
   - `.windsurfrules`配合Roo规则，定义项目的代码和文档生成规则。

7. **开发环境配置**:
   - `a7.code-workspace`定义VS Code的项目视图和配置。
   - `.cursor/`包含Cursor IDE的特定配置。
   - `.env.example`提供需要的环境变量配置模板。

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

1. **认证端点**:
   - `/api/token/` - 获取JWT认证令牌
   - `/api/token/refresh/` - 刷新JWT令牌
   - `/api/token/verify/` - 验证JWT令牌的有效性
   - `/api/token/blacklist/` - JWT令牌黑名单端点
   - `/api/login/` - 自定义登录端点，返回JWT令牌和用户信息
   - `/api/logout/` - 登出端点，使令牌失效

2. **用户管理API**:
   - `/api/users/` - 用户列表和创建
   - `/api/users/<id>/` - 用户详情、更新和删除
   - `/api/users/me/` - 获取当前登录用户信息
   - `/api/users/change_password/` - 修改当前用户密码
   - `/api/users/my_permissions/` - 获取当前用户的权限信息
   - `/api/roles/` - 角色列表和创建
   - `/api/roles/<id>/` - 角色详情、更新和删除
   - `/api/roles/<id>/permissions/` - 获取特定角色的权限信息

3. **核心API**:
   - `/api/health/` - 健康检查端点，提供API服务状态

4. **文档端点**:
   - `/swagger/` - Swagger UI API交互式文档
   - `/redoc/` - ReDoc 格式的API文档

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

## 管理和更新

此文件结构反映了项目的当前状态。随着项目的发展，将添加新的文件和目录，现有的可能会修改。建议定期更新本文档以保持其准确性。

当添加新的重要文件或目录时，请同时更新此文档中的映射、说明和关系部分。 