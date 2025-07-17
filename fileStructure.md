# 项目文件结构

## 目录结构映射

```
a7/                           # 项目根目录
├── .cursor/                  # Cursor IDE配置目录
│   ├── rules/                # 规则目录
│   │   ├── taskmaster/       # TaskMaster规则子目录
│   │   ├── cursor_rules.mdc  # Cursor规则文件
│   │   ├── self_improve.mdc  # 规则改进指南
│   │   ├── context7.mdc      # Context7规则
│   │   ├── file_structure.mdc # 文件结构规则
│   │   ├── taskmaster.mdc    # TaskMaster命令参考
│   │   └── dev_workflow.mdc  # 开发工作流指南
│   └── mcp.json              # Model Control Protocol配置
├── .taskmaster/              # TaskMaster工具目录
│   ├── tasks/                # 任务文件目录
│   │   ├── tasks.json        # 任务定义文件
│   │   ├── tasks.json.bak    # 任务定义备份
│   │   └── task_*.txt        # 各个任务详细文件
│   ├── task_done/            # 已完成任务目录
│   ├── docs/                 # 文档目录
│   │   ├── CurrentPlan.md    # 当前计划文档
│   │   └── prd.txt           # 产品需求文档
│   ├── reports/              # 报告目录
│   ├── templates/            # 模板目录
│   │   └── example_prd.txt   # 示例PRD模板
│   ├── config.json           # TaskMaster配置文件
│   └── state.json            # TaskMaster状态文件
├── a7/                       # Django项目主目录
│   ├── a7/                   # Django项目配置包
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── asgi.py           # ASGI应用配置
│   │   ├── settings.py       # Django设置文件
│   │   ├── urls.py           # URL路由配置，包含Swagger/ReDoc文档URL和JWT认证URL
│   │   └── wsgi.py           # WSGI应用配置
│   ├── marp_service/         # Marp服务应用
│   │   ├── __init__.py       # Python包初始化文件，包含主要转换函数
│   │   ├── apps.py           # 应用配置
│   │   ├── cli.py            # Marp命令行接口构建与执行
│   │   ├── exceptions.py     # 异常类定义
│   │   ├── serializers.py    # API序列化器
│   │   ├── temp.py           # 临时文件管理
│   │   ├── urls.py           # URL路由配置
│   │   ├── utils.py          # 工具函数
│   │   ├── validation.py     # Markdown验证模块
│   │   ├── views.py          # API视图
│   │   ├── themes/           # Marp主题目录
│   │   │   ├── hierarchy-default.css    # 默认层级主题
│   │   │   ├── hierarchy-minimalist.css # 极简层级主题
│   │   │   └── hierarchy-teaching.css   # 教学层级主题
│   │   ├── tests/           # 测试目录
│   │   ├── management/       # 管理命令目录
│   │   └── migrations/       # 数据库迁移目录
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
│   ├── ai_services/          # AI服务应用
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── admin.py          # AI服务的Admin配置
│   │   ├── apps.py           # 应用配置
│   │   ├── api_response.py   # 标准化API响应格式化工具
│   │   ├── models.py         # WebhookConfig和WebhookCallLog模型定义
│   │   ├── urls.py           # AI服务路由配置，包含StudentDialogueViewSet路由注册
│   │   ├── views.py          # AI服务视图和API实现，包含N8nWebhookAPIView和StudentDialogueViewSet
│   │   ├── services/         # 服务实现目录
│   │   │   ├── __init__.py              # Python包初始化文件
│   │   │   ├── base.py                  # 服务基类定义
│   │   │   ├── knowledge_converter.py   # AI响应到课程模型的转换器
│   │   │   ├── question_export.py       # 问题导出工具，支持JSON和CSV格式
│   │   │   ├── question_format.py       # 问题格式化工具
│   │   │   └── n8n_webhook/             # n8n Webhook服务目录
│   │   │       ├── __init__.py          # Python包初始化文件
│   │   │       ├── client.py            # N8nWebhookClient客户端实现，包含dialogue_with_student方法
│   │   │       ├── exceptions.py        # 异常类定义
│   │   │       └── formats.py           # 请求/响应格式定义，包含DialogueRequestData和DialogueResponseData模型
│   │   └── tests/                       # AI服务测试目录
│   │       ├── __init__.py                  # Python包初始化文件
│   │       ├── conftest.py                  # pytest配置文件
│   │       ├── test_client.py               # n8n客户端测试
│   │       ├── test_formats.py              # 数据格式模型测试
│   │       ├── test_knowledge_converter.py  # 数据转换器测试
│   │       ├── test_n8n_service.py          # n8n服务异步测试
│   │       ├── test_question_format.py      # 问题格式化工具测试
│   │       ├── test_real_n8n_integration.py # n8n真实集成测试
│   │       ├── test_student_dialogue.py     # 学生对话API单元测试
│   │       ├── test_student_dialogue_integration.py # 学生对话API集成测试
│   │       ├── test_views_integration.py    # AI服务视图集成测试
│   │       └── run_student_dialogue_tests.py # 学生对话测试运行脚本
│   ├── courses/              # 课程管理应用
│   │   ├── migrations/       # 数据库迁移文件
│   │   ├── tests/            # 测试目录
│   │   │   ├── test_question_export.py      # 问题导出测试
│   │   │   ├── test_question_export_integration.py # 问题导出集成测试
│   │   │   ├── test_api_exercises.py        # 练习题API测试
│   │   │   ├── test_api_exercises_additional.py # 练习题API补充测试
│   │   │   ├── test_progress_models.py      # 学习进度跟踪模型测试
│   │   │   ├── test_progress_serializers.py # 学习进度跟踪序列化器测试
│   │   │   ├── test_progress_tracking.py    # 学习进度跟踪API测试
│   │   │   └── test_file_storage.py         # 文件存储功能测试，验证文件上传、文件名唯一性、文件组织结构等
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── admin.py          # 课程Admin配置
│   │   ├── apps.py           # 应用配置
│   │   ├── models.py         # 课程模型定义
│   │   ├── serializers.py    # 课程序列化器
│   │   ├── serializers_ppt.py # 知识点到PPT转换序列化器
│   │   ├── serializers_progress.py # 学习进度跟踪序列化器
│   │   ├── storage.py        # 自定义文件存储类，实现文件名唯一化和按课程/文件类型组织文件
│   │   ├── urls.py           # 课程URL配置
│   │   ├── utils.py          # 工具函数，包含文件路径生成和文件验证函数
│   │   └── views.py          # 课程视图
│   ├── users/                # 用户管理应用
│   │   ├── migrations/       # 数据库迁移文件
│   │   ├── tests/            # 测试目录
│   │   │   ├── __init__.py   # 测试包初始化文件
│   │   │   └── test_jwt_middleware.py # JWT中间件测试
│   │   ├── management/       # 管理命令目录
│   │   │   ├── __init__.py   # 管理命令包初始化文件
│   │   │   └── commands/     # Django管理命令
│   │   │       ├── __init__.py # 命令包初始化文件
│   │   │       ├── init_roles.py # 初始化角色命令
│   │   │       └── sync_roles.py # 同步角色命令
│   │   ├── middleware/       # 中间件目录
│   │   │   ├── __init__.py   # 中间件包初始化文件
│   │   │   └── jwt_auth_middleware.py # JWT认证中间件
│   │   ├── __init__.py       # Python包初始化文件
│   │   ├── admin.py          # 用户Admin配置
│   │   ├── apps.py           # 应用配置
│   │   ├── models.py         # 用户和角色模型定义
│   │   ├── permission_utils.py # 权限工具函数
│   │   ├── permissions.py    # 权限类定义
│   │   ├── serializers.py    # 用户序列化器
│   │   ├── signals.py        # 信号处理器
│   │   ├── urls.py           # 用户URL配置
│   │   └── views.py          # 用户视图
├── .github/                  # GitHub配置目录
├── .git/                     # Git版本控制目录
├── .pytest_cache/            # Pytest缓存目录
├── tasks/                    # 任务文件目录（Task Master生成的任务）
├── test_html/                # 测试HTML文件目录
│   ├── auth_test.html        # 登录/登出/密码更改功能测试页面
│   ├── permissions_test.html # 角色权限测试页面
│   └── ppt_direct_download_test.html # 知识点到PPT直接下载功能测试页面
├── pptx_output/              # 知识点到PPT转换输出目录，存储生成的PPTX文件
├── marp_test_output/         # Marp集成测试输出目录
│   ├── default_theme/        # 默认主题测试输出
│   │   ├── default_hierarchy_theme.html  # HTML格式输出
│   │   ├── default_hierarchy_theme.pdf   # PDF格式输出
│   │   └── default_hierarchy_theme.pptx  # PPTX格式输出
│   ├── minimalist_theme/     # 极简主题测试输出
│   ├── teaching_theme/       # 教学主题测试输出
│   └── style_options/        # 样式选项测试输出
├── api_test_output/          # API测试输出目录，存储测试结果和生成的文件
├── test_api.py               # API测试脚本，用于测试中间件功能
├── test_api_question.py      # API测试脚本，用于测试问题生成API
├── marp_integration_test.py  # 手动集成测试脚本，测试知识点到PPT的完整流程
├── api_test_runner.py        # API端到端测试运行脚本，测试各种格式的直接下载功能
├── .gitignore                # Git忽略配置文件
├── .roomodes                 # Roo模式配置文件
├── .windsurfrules            # Windsurf规则配置文件
├── a7.code-workspace         # VS Code工作区配置文件
├── context7_library.md       # Context7库ID记录文件
├── CurrentPlan.md            # 当前项目计划文档
├── fileStructure.md          # 项目文件结构文档（本文件）
├── jwt_auth.log              # JWT认证日志文件
├── old_ai_servers.md         # 旧AI服务器文档
├── permission.log            # 权限检查日志文件
├── request.log               # 请求日志文件
└── requirements.txt          # 项目依赖文件
```

## 项目目录中的特殊文件夹

- **a7/presentations/**: 演示文稿存储目录，用于保存知识点生成的演示文稿文件
- **a7/tmp/**: 临时文件目录，存储处理过程中的临时文件
- **a7/static/**: 静态文件存储目录，包含项目使用的静态资源文件，包括presentations子目录
- **a7/marp_test_output/**: 项目级Marp测试输出目录，存储在a7目录中进行的测试生成的文件
- **a7/media/**: 媒体文件存储目录，用于保存用户上传的文件，如课件相关文件，按课程ID和文件类型组织目录结构

## 文件用途说明

### Docker部署相关文件

- **a7/Dockerfile**: Docker容器构建配置文件，定义了基于Python 3.13.3的应用容器。使用非特权用户运行应用以提高安全性，配置了Python环境变量防止生成缓存文件，安装依赖并暴露8000端口。
- **a7/compose.yaml**: Docker Compose服务配置文件，定义了应用服务的构建和运行方式。暴露8000端口到主机，并包含了PostgreSQL数据库集成的注释示例代码。
- **a7/README.Docker.md**: Docker部署和使用说明文档，提供了如何构建和运行Docker容器的指导，包括本地开发和云部署说明。
- **a7/.dockerignore**: Docker构建过程中要忽略的文件列表，用于排除不需要包含在Docker镜像中的文件，优化构建过程和减小镜像大小。

### Django项目文件

- **a7/a7/__init__.py**: Python包标识文件，表明该目录是一个Python包。
- **a7/a7/asgi.py**: ASGI（异步服务器网关接口）应用配置，用于异步服务器部署。
- **a7/a7/settings.py**: Django项目的核心配置文件，包含数据库、应用、中间件等设置。包含完整的Django REST Framework配置，定义了API认证（会话认证，JWT令牌认证已启用）、权限控制、分页（每页20条）、渲染器（JSON和可视化API）、解析器、异常处理、过滤（已配置DjangoFilterBackend作为默认过滤后端）、版本控制、JSON格式和时间格式等全局设置。新增MEDIA_ROOT和MEDIA_URL配置，支持文件上传和存储功能。新增文件上传配置（最大内存大小、文件权限等）和允许的文件类型列表。
- **a7/a7/urls.py**: URL路由配置，定义请求路径与视图函数的映射关系。新增媒体文件URL配置，在开发环境中支持通过/media/路径访问上传的文件。
- **a7/a7/wsgi.py**: WSGI（Web服务器网关接口）应用配置，用于传统Web服务器部署。
- **a7/manage.py**: Django命令行工具，用于执行各种管理任务，如运行开发服务器、数据库迁移等。
- **a7/db.sqlite3**: SQLite数据库文件，存储项目的所有数据，包括用户、角色、权限、课程、知识点等实体数据。在开发环境中使用，包含测试和示例数据。
- **a7/permission.log**: 项目级权限检查日志文件，记录权限中间件在a7目录下的日志。

### 文件存储相关文件

- **a7/courses/storage.py**: 自定义文件存储类，继承自Django的FileSystemStorage，实现文件名唯一化（使用UUID）和按课程/文件类型组织文件结构的功能。重写了get_available_name和get_valid_name方法，确保文件名唯一性并保留文件路径结构。
- **a7/courses/utils.py**: 工具函数文件，包含courseware_file_path函数（生成按课程ID和文件类型组织的文件路径）、get_simple_file_type函数（从MIME类型获取简化的文件类型分类）、validate_file_type函数（验证文件类型是否在允许列表中）和validate_file_size函数（验证文件大小是否超过限制）。
- **a7/courses/models.py**: 包含CoursewareFile模型，用于存储课件文件的元数据（文件名、大小、类型、上传时间等），并使用自定义存储类和文件路径生成函数。添加了get_file_url方法获取文件URL和validate_file方法验证文件类型和大小。
- **a7/courses/tests/test_file_storage.py**: 文件存储功能的测试文件，验证文件上传、文件名唯一性、文件组织结构、文件验证功能和文件URL生成。

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
- **a7/users/middleware/jwt_auth_middleware.py**: JWT认证中间件（已启用），负责验证JWT令牌、记录认证过程和处理无效令牌情况。

### 用户管理应用文件

- **a7/users/__init__.py**: Users应用的Python包标识文件。
- **a7/users/admin.py**: Django Admin后台配置，定义用户和角色模型在管理界面的展示方式和操作功能。
- **a7/users/apps.py**: 应用配置文件，包含应用元数据和启动逻辑。
- **a7/users/models.py**: 模型定义，包含扩展的User模型和Role模型，实现基于角色的用户模型和权限系统。
- **a7/users/permissions.py**: 自定义权限类，定义基于角色和功能的权限类，如IsAdmin、IsTeacher、IsAdminOrTeacher等。新增AllowAll权限类，允许所有请求访问，无需验证权限。
- **a7/users/permission_utils.py**: 权限工具函数，提供权限分配、管理和同步功能，实现基于角色的权限自动分配。
- **a7/users/middleware/jwt_auth_middleware.py**: JWT认证中间件（已启用），负责验证JWT令牌、记录认证过程和处理无效令牌情况。
- **a7/users/signals.py**: 信号处理器，包含用户创建时自动生成令牌和分配权限的逻辑，以及角色和权限变更的处理。
- **a7/users/tests/test_jwt_middleware.py**: JWT中间件测试文件，包含对JWTAuthMiddleware的单元测试，验证令牌验证、过期令牌处理和认证日志记录功能。
- **a7/users/urls.py**: URL路由配置，定义用户API端点，包括用户管理、角色管理、登录和登出端点。
- **a7/users/views.py**: 视图文件，包含UserViewSet（含权限控制）和RoleViewSet视图集，自定义的认证视图（CustomTokenObtainPairView和装饰类），以及登出视图（LogoutView）。还包括完整的Swagger文档装饰类（DecoratedTokenObtainPairView、DecoratedTokenRefreshView、DecoratedTokenVerifyView、DecoratedTokenBlacklistView）。使用OpenAPI Schema定义视图响应格式，确保Swagger文档生成正确。
- **a7/users/management/commands/init_roles.py**: 管理命令，用于初始化角色和权限，并更新现有用户的权限设置。
- **a7/users/management/commands/sync_roles.py**: 管理命令，用于同步用户角色和权限数据，修复数据不一致问题。

### 课程管理应用文件

- **a7/courses/__init__.py**: Courses应用的Python包标识文件。
- **a7/courses/admin.py**: 课程相关模型的Admin配置，定义Course、KnowledgePoint、Courseware、CoursewareFile、Exercise、StudentAnswer和LearningRecord模型在管理界面的展示方式和操作功能。添加了CoursewareFile的Admin配置，支持文件元数据的管理。
- **a7/courses/apps.py**: 课程应用配置文件，包含应用元数据和中文名称设置。
- **a7/courses/models.py**: 模型定义，包含Course（课程）、KnowledgePoint（知识点）、Courseware（课件）、CoursewareFile（课件文件）、Exercise（练习题）、StudentAnswer（学生答案）和LearningRecord（学习记录）模型，实现课程内容管理、练习评测系统和学习进度跟踪功能。新增CourseProgress（课程进度）模型，跟踪学生整体课程完成情况，包括总体进度、必修内容完成状态、正确率和总学习时间。CoursewareFile模型存储课件相关文件的元数据，包括文件名、大小、类型和上传时间，并通过Courseware的has_files字段表示课件是否有相关文件。
- **a7/courses/serializers.py**: 课程序列化器定义，包含CourseSerializer（读取）、CourseCreateSerializer（创建）、CourseUpdateSerializer（更新）和CourseGenerationSerializer（AI内容生成请求）类，负责课程数据的序列化与反序列化。还包含KnowledgePointSerializer（读取，含课程标题、父知识点标题和子知识点列表）、KnowledgePointCreateSerializer（创建，含父知识点属于同一课程的验证）和KnowledgePointUpdateSerializer（更新，含循环引用和跨课程引用验证）类，负责知识点数据的序列化与反序列化。实现了验证方法（validate_title、validate_subject等），确保数据有效性和一致性。还包含QuestionGenerationSerializer，用于问题生成API的请求参数验证。新增Exercise和StudentAnswer相关序列化器（读取、创建、更新、反馈），支持练习题和学生答案管理。
- **a7/courses/permissions.py**: 课程权限类定义，包含IsTeacherOrAdmin（教师或管理员权限）和IsCourseTeacherOrAdmin（课程教师或管理员权限）类，负责课程API的权限控制。还包含IsKnowledgePointCourseTeacherOrAdmin权限类，确保只有知识点所属课程的教师或管理员可以修改或删除知识点。
- **a7/courses/urls.py**: 课程应用的URL路由配置，使用`DefaultRouter`注册`CourseViewSet`、`KnowledgePointViewSet`、`CoursewareViewSet`、`CourseContentGenerationViewSet`、`QuestionGenerationViewSet`、`ExerciseViewSet`和`StudentAnswerViewSet`，提供课程内容、练习和答案的API端点。
- **a7/courses/views.py**: 课程相关的视图文件，包含`CourseViewSet`, `KnowledgePointViewSet`, `CoursewareViewSet`, `CourseContentGenerationViewSet`, `QuestionGenerationViewSet`, `ExerciseViewSet` 和 `StudentAnswerViewSet` 视图集，实现课程、知识点、课件、练习题和学生答案的CRUD操作和AI内容生成功能。新增`ProgressTrackingViewSet`视图集，提供学习进度跟踪API端点，包括course-progress（获取课程进度）、knowledge-point-progress（获取知识点进度）、update-learning-record（更新学习记录）和student-summary（获取学生进度概览）。`CourseViewSet`配置了`IsAuthenticated`权限类，要求用户认证才能访问，并针对不同操作类型设置了更具体的权限控制。特别是`my_courses`方法现在确保只返回当前认证用户创建的课程，而不是任何用户的课程。`ExerciseViewSet`和`StudentAnswerViewSet`配置了过滤、排序和搜索功能，支持按知识点、题型、难度等字段过滤，按创建时间、难度等字段排序，以及按标题、内容等字段搜索。
- **a7/courses/validations.py**: 通用验证工具类，提供了字段验证（validate_text_field）、对象存在性验证（validate_existence）和唯一性验证（validate_uniqueness）等方法，为序列化器提供复用的验证逻辑。
- **a7/courses/utils.py**: 工具函数文件，包含validate_required_params函数，用于验证请求中必需的参数是否存在，支持GET和POST/PUT/PATCH请求，适用于自定义操作和视图方法。
- **a7/courses/tests.py**: 测试文件，包含课程模型的单元测试，验证模型创建、关系和功能正确性，以及练习题、学生答案和学习记录的测试用例。
- **a7/courses/tests_serializers.py**: 序列化器测试文件，包含对ExerciseSerializer和StudentAnswerSerializer相关类的单元测试，验证数据序列化、反序列化和验证逻辑的正确性。
- **a7/courses/tests_api.py**: 课程API测试文件，包含API接口的功能测试，验证权限控制、CRUD操作和自定义操作的正确性，包括KnowledgePointAPITests测试类，验证知识点API的功能完整性和权限控制。
- **a7/courses/tests_api_new.py**: 课程内容管理API的全面测试套件，包含CourseAPITests（验证课程CRUD和权限控制）、KnowledgePointAPITests（测试知识点层级结构和循环引用防护）、CoursewareAPITests（测试课件管理功能）和CourseContentGenerationAPITests（测试AI内容生成）四个主要测试类。共实现42个全面测试用例，验证不同用户角色（管理员、教师、学生）的权限控制、所有API端点的功能完整性以及特殊操作如my_courses、top_level、children和by_course等。测试包含边界情况处理、数据验证和错误响应。
- **a7/courses/tests_validation.py**: 验证逻辑测试文件，包含对课程、知识点和课件API的验证逻辑测试，验证字段验证、唯一性检查、关系完整性（如循环引用检测）等验证功能的正确性。测试不同场景下的验证行为，确保数据一致性和业务规则的强制执行。
- **a7/courses/migrations/**: 包含课程模型的数据库迁移文件，记录模型结构的变更历史。
#### 问题和练习测试
- **a7/courses/tests/test_api_questions.py**: 问题生成API的测试，验证API端点功能、参数验证、授权和错误处理，确保通过API生成问题的完整流程正常工作。
- **a7/courses/tests/test_question_export.py**: 问题导出工具的单元测试，验证JSON和CSV格式导出功能、文件名生成、内容类型设置和错误处理。包含QuestionExportToolTests和QuestionExportAPITests两个测试类，共9个测试用例。
- **a7/courses/tests/test_question_export_integration.py**: 问题导出功能的集成测试，验证从问题生成到导出的完整流程。使用模拟技术测试API响应、会话存储和多种格式导出。
- **a7/courses/tests/test_api_exercises.py**: 练习题和学生答案API的CRUD功能测试，包括对过滤、排序和搜索功能的全面测试用例，验证按知识点过滤、按创建时间排序、按内容搜索等功能的正确性。
- **a7/courses/tests/test_api_exercises_additional.py**: 练习题和学生答案API的补充测试文件，包含以下测试类：
  - **ExerciseValidationTests**: 字段验证和边缘情况测试，验证题型、难度、必填字段等验证逻辑
  - **StudentAnswerValidationTests**: 学生答案约束测试，验证唯一性约束和分数范围验证
  - **CombinedFilteringTests**: 组合过滤和排序测试，验证多条件筛选和多字段排序功能
  - **PaginationAndEdgeCaseTests**: 分页和边缘情况测试，验证分页、无效页码、特殊字符处理等
  - **APIResponseFormatTests**: API响应格式测试，验证列表、详情、错误响应和创建响应的标准格式

#### 学习进度测试
- **a7/courses/tests/test_progress_models.py**: 学习进度跟踪模型的单元测试，验证CourseProgress和LearningRecord模型的功能、状态转换和数据完整性。
- **a7/courses/tests/test_progress_serializers.py**: 学习进度序列化器的单元测试，验证序列化、反序列化、验证逻辑和字段保护功能。
- **a7/courses/tests/test_progress_tracking.py**: 学习进度跟踪API的功能测试，验证进度查询、更新和统计功能，以及权限控制和数据一致性。
- **a7/courses/tests/test_courseware_file.py**: 课件文件模型的单元测试，验证文件元数据存储、文件类型自动检测、文件管理和Courseware模型的has_files状态自动更新功能。测试覆盖文件创建、删除以及多文件管理场景。

#### 知识点到演示文稿转换测试
- **a7/courses/tests/test_knowledge_to_ppt_api.py**: 知识点到PPT转换API的全面测试，验证参数验证、授权、响应格式和错误处理。
- **a7/courses/tests/test_knowledge_to_ppt_service.py**: 知识点到PPT转换服务的单元测试，验证服务的核心功能、配置选项和输出格式。
- **a7/courses/tests/test_knowledge_to_ppt_conversion.py**: 知识点转换为Markdown的功能测试，验证内容格式化、层级结构和元数据处理。
- **a7/courses/tests/test_knowledge_to_ppt_integration.py**: 完整转换流程的集成测试，验证从知识点数据到最终演示文稿的全流程。
- **a7/courses/tests/test_knowledge_to_ppt_real.py**: 使用真实数据的转换测试，验证在实际环境下的转换结果和性能表现。
- **a7/courses/tests/test_knowledge_to_ppt_direct_download.py**: 直接下载功能测试，验证Content-Type设置、文件名处理和响应头配置。
- **a7/courses/tests/test_markdown_validation_integration.py**: Markdown验证与修复功能的集成测试，验证自动修正和格式规范化功能。
- **a7/courses/serializers_ppt.py**: 知识点到PPT转换序列化器定义，包含KnowledgePointToPPTSerializer类，负责验证知识点转PPT所需的各项参数，包括必填的knowledge_point_ids（知识点ID列表）和可选参数如include_children（是否包含子知识点）、max_depth（包含子知识点的最大深度）、format（输出格式，支持pptx/pdf/html）、theme（演示主题）等。实现了validate_knowledge_point_ids方法检查ID重复，以及validate方法进行整体数据验证。新增direct_download和filename字段，支持直接下载功能，启用后将文件直接作为响应返回，并使用指定的文件名。
- **a7/courses/serializers_progress.py**: 学习进度跟踪相关序列化器定义，包含KnowledgePointProgressSerializer、ExerciseProgressSerializer、StudentAnswerSerializer、LearningRecordSerializer、LearningRecordUpdateSerializer、CourseProgressSerializer和CourseProgressDetailSerializer类，实现进度数据的序列化与反序列化，支持字段验证和只读保护。
- **a7/courses/services/progress_tracker.py**: 进度跟踪服务实现，提供ProgressTrackerService类，负责更新练习题统计信息、知识点进度和课程整体进度，以及获取学生进度概览。实现了三个核心方法：update_exercise_statistics（更新练习题统计信息）、update_knowledge_point_progress（更新知识点进度）和update_course_progress（更新课程整体进度），以及get_student_progress（获取学生进度概览）。

### AI服务应用文件

- **a7/ai_services/__init__.py**: AI服务应用的Python包标识文件。
- **a7/ai_services/admin.py**: Django Admin配置，定义WebhookConfig和WebhookCallLog模型在管理界面的展示与操作方式。
- **a7/ai_services/apps.py**: 应用配置文件，包含应用元数据和启动逻辑。
- **a7/ai_services/api_response.py**: 标准化API响应格式化工具，提供`create_api_response`函数用于生成统一的API响应。
- **a7/ai_services/models.py**: 模型定义，包含WebhookConfig（webhook配置）和WebhookCallLog（调用日志）模型，实现与外部服务集成和调用记录功能。
- **a7/ai_services/urls.py**: URL路由配置，定义AI服务的API端点路径，包含StudentDialogueViewSet的路由注册。
- **a7/ai_services/views.py**: 视图文件，包含N8nWebhookAPIView视图类和StudentDialogueViewSet视图集，处理webhook请求、学生对话请求，并转发至n8n服务，使用标准化的响应格式。新增ExerciseGenerationViewSet视图集，实现练习题生成API，允许匿名访问，支持根据查询文本、知识点ID、题型、数量和难度生成练习题，但不将生成的练习题保存到数据库。新增StudentAnswerCorrectionSerializer和StudentAnswerCorrectionViewSet，实现学生答案校正API，允许匿名访问，支持根据练习题ID和学生答案评估正确性并提供结构化反馈，包括正确性、得分、反馈意见、改进建议和解析说明。
- **a7/ai_services/services/knowledge_converter.py**: 负责将AI服务（如n8n）返回的课程内容JSON数据，安全地转换为数据库中的Course和KnowledgePoint模型。包含对输入数据进行验证、处理层级结构（有深度限制以防无限递归）、以及在原子事务中完成数据库操作的健壮逻辑。
- **a7/ai_services/services/question_export.py**: 问题导出工具类，提供将AI生成的问题导出为JSON和CSV格式的功能。实现了优雅的文件名生成、Unicode字符处理和大型数据集优化。包含QuestionExporter类，提供export_as_json、export_as_csv和通用export_questions方法。
- **a7/ai_services/services/base.py**: 服务基类定义，提供共享的服务功能和接口。
- **a7/ai_services/services/question_format.py**: 问题格式化工具，提供标准化问题格式的功能。

### n8n Webhook服务文件

- **a7/ai_services/services/n8n_webhook/client.py**: N8nWebhookClient实现，提供异步HTTP客户端用于调用n8n webhook服务，包含请求/响应验证逻辑及各类功能的便捷方法：
  - **课程内容生成方法**（generate_course_content、generate_course_content_sync）
  - **问题生成方法**（generate_questions、generate_questions_sync）
  - **学生对话方法**（dialogue_with_student、dialogue_with_student_sync）
  - **答案校正方法**（correct_student_answer、correct_student_answer_sync）
  - **练习题生成方法**（generate_exercises、generate_exercises_sync）
  - **知识点转Markdown方法**（generate_markdown_from_knowledge）
  - 所有方法均提供同步和异步两种版本，简化调用流程
  
- **a7/ai_services/services/n8n_webhook/exceptions.py**: 自定义异常类定义，构建完整异常层次结构：
  - **N8nWebhookError** 作为基类
  - **N8nConnectionError**（连接错误）
  - **N8nTimeoutError**（超时错误）
  - **N8nResponseError**（响应错误）
  - **N8nValidationError**（请求/响应验证相关异常）
  - 提供详细的错误信息和处理机制，增强系统健壮性
  
- **a7/ai_services/services/n8n_webhook/formats.py**: 使用Pydantic定义全面的请求/响应数据模型：
  - **课程内容生成相关模型** (CourseGenerationRequestData、CourseGenerationResponseData)
  - **问题生成相关模型** (QuestionGenerationRequestData、QuestionData、QuestionGenerationResponseData)
  - **学生对话相关模型** (DialogueRequestData、DialogueResource、DialogueResponseData)
  - **练习题生成相关模型** (ExerciseGenerationRequestData、ExerciseGenerationResponseData)
  - **答案校正相关模型** (AnswerCorrectionRequestData、AnswerCorrectionResponseData)
  - **知识点转Markdown相关模型** (MarkdownGenerationRequestData、MarkdownGenerationResponseData)
  - **多种解析函数**，如parse_exercise_text、parse_single_exercise、format_answer_correction_response等
  - 题型格式统一使用下划线格式（如"single_choice"、"multiple_choice"），确保系统一致性
  
- **a7/ai_services/services/n8n_webhook/prompt_templates.py**: 定义各种AI任务的提示模板：
  - 为不同任务类型提供结构化的提示模板
  - 包含模板参数替换和格式化功能
  - 实现提示模板的版本控制和选择机制
  
- **a7/ai_services/services/n8n_webhook/response_processor.py**: 负责处理AI服务返回的响应：
  - 实现响应解析和验证逻辑
  - 处理各种格式的AI输出（JSON、markdown、结构化文本等）
  - 转换AI响应为标准化的数据格式
  
- **a7/ai_services/services/n8n_webhook/logger.py**: 实现N8N服务日志记录：
  - 提供专门的日志记录器
  - 记录请求、响应和错误信息
  - 支持可配置的日志级别

### AI服务测试文件

- **a7/ai_services/tests/__init__.py**: AI服务测试包标识文件。
- **a7/ai_services/tests/conftest.py**: pytest配置文件，包含测试固件（fixtures）、事件循环配置、测试标记注册以及全局测试设置。
- **a7/ai_services/tests/individual_tests/**: 包含独立测试脚本的目录，便于隔离测试特定功能。

#### 基础组件测试
- **a7/ai_services/tests/test_client.py**: n8n webhook客户端测试，主要测试客户端的基本功能和错误处理。
- **a7/ai_services/tests/test_formats.py**: n8n webhook数据格式(Pydantic模型)的单元测试，验证数据模型的验证逻辑和字段类型转换。
- **a7/ai_services/tests/test_knowledge_converter.py**: knowledge_converter模块的单元测试，验证JSON到Django模型的转换逻辑、数据验证、递归深度限制和数据库操作的原子性（事务回滚）。
- **a7/ai_services/tests/test_n8n_service.py**: n8n Webhook服务的异步测试实现。包含使用模拟(mock)数据的单元测试和针对真实n8n环境的集成测试，以验证端到端的功能。
- **a7/ai_services/tests/test_prompt_templates.py**: 测试提示模板的正确生成、参数替换和格式化功能。
- **a7/ai_services/tests/test_format_responses.py**: 测试AI响应的格式化和解析功能，确保系统能正确处理各种格式的AI输出。
- **a7/ai_services/tests/test_response_parsing.py**: 测试响应解析逻辑，验证系统能从各种AI输出格式中提取结构化信息。
- **a7/ai_services/tests/test_question_format.py**: 问题格式化工具的单元测试，验证问题格式转换和处理功能。
- **a7/ai_services/tests/test_views_integration.py**: N8nWebhookAPIView的集成测试，验证从API接收请求到数据持久化的完整流程。

#### 功能集成测试
- **a7/ai_services/tests/test_real_n8n_integration.py**: 与真实n8n服务的基础集成测试，验证连接、通信和响应处理。
- **a7/ai_services/tests/test_generate_course_content_integration.py**: 测试课程内容生成功能的集成测试，验证与n8n服务的交互和响应处理。
- **a7/ai_services/tests/test_generate_markdown_from_knowledge_integration.py**: 知识点转Markdown功能的集成测试，验证转换过程和输出格式的正确性。
- **a7/ai_services/tests/test_generate_questions_integration.py**: 问题生成功能的集成测试，验证基于知识点内容生成问题的完整流程。
- **a7/ai_services/tests/test_knowledge_point_to_ppt_integration.py**: 知识点到PPT转换功能的集成测试，验证从知识点数据到演示文稿的完整流程。

#### 学生互动功能测试
- **a7/ai_services/tests/test_student_dialogue.py**: 学生对话API的单元测试，包含序列化器测试、数据模型测试和API端点测试，使用模拟对象替代真实的n8n服务。
- **a7/ai_services/tests/test_student_dialogue_integration.py**: 学生对话API的集成测试，包含与真实n8n服务的交互测试和错误处理测试，验证单轮对话和多轮对话功能。
- **a7/ai_services/tests/test_student_assistant_integration.py**: 学生助手功能的全面集成测试，验证复杂场景下的响应质量和系统稳定性。
- **a7/ai_services/tests/test_exercise_generation.py**: 练习题生成API的单元测试，包含对API端点的功能测试、参数验证测试和错误处理测试。
- **a7/ai_services/tests/test_exercise_generation_integration.py**: 练习题生成API的集成测试，包含与真实N8N服务的交互测试，验证生成不同类型和难度的练习题。
- **a7/ai_services/tests/test_answer_correction.py**: 学生答案校正API的单元测试，验证API端点功能、参数验证和错误处理。
- **a7/ai_services/tests/test_answer_correction_integration.py**: 学生答案校正API的集成测试，包含评估不同类型（单选题、多选题、简答题）学生答案的功能测试。

#### 测试运行脚本
- **a7/ai_services/tests/run_integration_tests.py**: 集成测试运行脚本，提供统一的方式运行所有集成测试。
- **a7/ai_services/tests/run_student_assistant_tests.py**: 学生助手功能测试运行脚本，提供便捷的方式测试学生交互相关功能。

### pytest配置文件

- **a7/pytest.ini**: pytest测试框架配置文件，定义Django集成配置、异步测试模式设置、自定义测试标记以及日志输出格式配置。重点配置了asyncio_mode=strict确保异步测试的严格模式，以及asyncio_default_fixture_loop_scope设置事件循环作用域。

### 测试文件

- **test_html/auth_test.html**: 用于测试登录/登出/密码更改功能的HTML页面，提供基本UI和JavaScript测试代码，通过浏览器直接测试认证API。
- **test_html/permissions_test.html**: 角色权限测试页面，用于测试不同角色用户的权限访问控制，支持多角色登录和API权限验证。
- **a7/users/tests.py**: 包含完整的自动化测试套件，测试认证功能（登录、登出、密码更改）、基于角色的权限控制以及完整的用户流程端到端测试。
- **a7/courses/tests.py**: 包含课程模型的自动化测试，验证课程内容管理功能的正确性，以及练习题、学生答案和学习记录的功能测试，包括学习进度跟踪、状态转换和统计分析测试。
- **a7/apps/core/tests.py**: 包含核心模型的自动化测试，验证用户活动跟踪和系统性能监控功能，测试JSON字段处理方法和真实应用场景模拟。
- **a7/apps/core/tests/test_middleware.py**: 核心中间件测试文件，包含对RequestLoggingMiddleware和RequestProcessorMiddleware的单元测试，验证路径排除、日志记录、请求验证、响应处理和请求大小限制功能。
- **test_api.py**: API测试脚本，用于集成测试中间件功能，包括JWT认证、请求日志和请求处理。提供实际HTTP请求测试，验证中间件在真实环境中的表现。
- **marp_integration_test.py**: 手动集成测试脚本，用于测试知识点到PPT的完整流程，包括知识点数据准备、Markdown生成（支持本地和AI两种模式）、Markdown验证和修复、以及转换为演示文稿（支持pptx/pdf/html格式）。脚本设计为可通过命令行参数配置，提供详细的日志记录，并保存所有中间文件用于分析和调试。
- **test_html/ppt_direct_download_test.html**: 知识点到PPT直接下载功能测试页面，提供基本UI和JavaScript测试代码，通过浏览器直接测试知识点到PPT转换API的直接下载功能，支持PPTX、PDF和HTML格式的直接下载测试。
- **api_test_runner.py**: API端到端测试运行脚本，用于测试知识点到PPT转换API的直接下载功能和Base64内容返回功能。支持多种格式(PPTX/PDF/HTML)的转换测试，并生成详细的HTML格式测试报告。测量各种格式转换的性能指标，包括响应时间和文件大小，提供测试结果的可视化展示，并支持批量测试多种格式和多种主题的组合。
- **api_test_output/**: API测试输出目录，存储API测试运行脚本生成的测试报告，包括HTML格式的测试结果报告和性能指标图表。

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

- **marp_test_output/**: 存储Marp集成测试生成的文件，用于分析和调试知识点到PPT转换的完整流程。
  - **default_theme/**: 默认主题测试输出，包含HTML、PDF和PPTX格式的文件，使用默认层级主题。
  - **minimalist_theme/**: 极简主题测试输出，包含使用极简层级主题的各种格式文件。
  - **teaching_theme/**: 教学主题测试输出，包含使用教学层级主题的各种格式文件。
  - **style_options/**: 样式选项测试输出，包含使用不同颜色方案的测试结果。

- **api_test_output/**: API测试输出目录，存储API测试过程中生成的文件和测试报告。
  - 包含各种格式的演示文稿文件（以UUID命名，如`presentation_*.pptx/pdf/html`）
  - 包含测试下载文件（命名格式如`test_download_*.pptx/pdf/html`）
  - 包含HTML格式的测试报告（如`test_report_*.html`）
  - 包含用于测试的占位文件（`placeholder_presentation_*.pptx/pdf/html`）

- **pptx_output/**: 知识点到PPT转换输出目录，存储生成的PPTX文件，用于正式环境下的演示文稿保存和分享。

### 文档文件

- **fileStructure.md**: 本文档，提供项目文件和目录的完整映射及其用途。
- **prd.txt**: 产品需求文档(PRD)，描述项目功能、技术架构、开发路线图和系统需求，用于Task Master生成任务。

## 关键文件之间的关系

1. **Django项目结构**:
   - `a7/a7/settings.py`定义Django项目的核心配置，如数据库连接、安装的应用等。
   - `a7/a7/settings.py`中的`REST_FRAMEWORK`字典配置REST API框架的全局行为，包括认证、权限、分页、渲染器、解析器、异常处理、过滤（配置了DjangoFilterBackend作为默认过滤后端）、版本控制、JSON格式和时间格式等全局设置。
   - `a7/a7/urls.py`配置URL路由，将请求映射到对应的视图函数。
   - `a7/a7/asgi.py`和`a7/a7/wsgi.py`提供异步和同步Web服务器网关接口。
   - `a7/manage.py`是命令行工具入口，用于执行Django管理命令。
   - `a7/apps/core/urls.py`定义核心应用的URL路径，被主urls.py文件包含。
   - `a7/apps/core/views.py`实现API端点的视图逻辑，如健康检查接口。

2. **用户认证与授权系统**:
   - `a7/users/models.py`定义自定义User模型和Role模型，是系统权限设计的基础，实现基于角色的用户模型和权限系统。
   - `a7/users/permissions.py`实现细粒度的权限控制系统，包含多种基于角色和功能的权限类，但目前系统已添加并启用了`AllowAll`权限类，允许所有请求无需验证即可访问。
   - `a7/users/middleware/jwt_auth_middleware.py`实现JWT认证中间件，但目前已在settings.py中禁用，不再对请求进行令牌验证。
   - `a7/users/signals.py`处理用户创建、角色变更和权限同步的信号，确保权限系统的一致性。
   - `a7/users/management/commands/init_roles.py`提供管理命令初始化角色和权限数据。
   - `a7/users/management/commands/sync_roles.py`提供管理命令同步用户角色和权限数据，修复数据不一致问题。
   - `a7/users/serializers.py`实现数据转换，支持REST API的用户数据处理，包含密码更改的验证逻辑以及各种令牌响应的序列化器（为Swagger/ReDoc文档提供示例）。
   - `a7/users/views.py`提供用户和角色管理的API端点，以及登录/登出/密码更改功能，并使用权限类控制访问。该文件还包括增强的JWT令牌视图实现，通过装饰器模式为Swagger文档提供标准化响应，以及令牌验证和黑名单功能。
   - `a7/users/urls.py`定义用户API路由，被主urls.py包含，负责将请求路由到对应的视图函数。
   - `a7/a7/urls.py`定义顶级URL路由，集成JWT认证端点(`/api/token/`, `/api/token/refresh/`, `/api/token/verify/`, `/api/token/blacklist/`)以及各应用的URL配置。
   - `a7/a7/settings.py`中的`AUTH_USER_MODEL`设置指向自定义User模型，还包含MIDDLEWARE配置中的权限中间件和日志配置。
   - `a7/a7/settings.py`中的`SIMPLE_JWT`配置定义JWT令牌的行为，包括黑名单和令牌轮换设置。
   - `a7/a7/settings.py`中的`REST_FRAMEWORK`配置已修改，`DEFAULT_AUTHENTICATION_CLASSES`移除了JWT认证，`DEFAULT_PERMISSION_CLASSES`设置为`AllowAny`，允许所有请求无需认证即可访问API。
   - `a7/users/tests.py`提供认证和权限功能的自动化测试，确保系统按预期工作。
   - `test_html/auth_test.html`和`test_html/permissions_test.html`提供基于浏览器的手动测试界面，验证API交互。
   - `permission.log`记录权限中间件的访问检查日志，帮助调试和监控权限系统。

3. **课程内容管理系统**:
   - `a7/courses/models.py`定义Course、KnowledgePoint、Courseware、Exercise、StudentAnswer和LearningRecord模型，实现课程内容的组织和管理以及练习评测功能。
   - `a7/courses/admin.py`配置课程相关模型在Django Admin中的展示和操作方式。
   - `a7/courses/tests.py`提供课程模型的自动化测试，验证课程内容管理功能的正确性，以及练习题、学生答案和学习记录的功能测试。
   - `a7/courses/serializers.py`定义序列化器，将课程和知识点模型转换为JSON格式以支持API接口，包括课程相关的序列化器实现自动设置当前用户为教师，知识点序列化器实现层级结构的展示和验证（包括防止循环引用和跨课程引用）。
   - `a7/courses/permissions.py`定义权限类，实现基于角色和所有权的访问控制，但当前项目已配置为使用`AllowAll`权限类，忽略这些权限限制。
   - `a7/courses/views.py`实现`CourseViewSet`, `KnowledgePointViewSet`, `CoursewareViewSet`, `ExerciseViewSet` 和 `StudentAnswerViewSet`视图集。所有视图的permission_classes已设置为`[AllowAll]`或未设置，允许无需认证即可访问所有API端点。
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

4. **TaskMaster相关**:
   - `.taskmaster/config.json`定义TaskMaster的配置信息，包括使用的AI模型和参数设置。
   - `.taskmaster/state.json`记录TaskMaster的当前状态信息。
   - `.taskmaster/templates/example_prd.txt`提供用于生成任务的PRD模板。
   - `.taskmaster/docs/prd.txt`是基于示例创建的实际产品需求文档，用于任务生成。
   - `.taskmaster/tasks/tasks.json`存储所有任务的定义和元数据。
   - `.taskmaster/tasks/task_*.txt`为每个任务提供详细描述和实现指南。
   - `.taskmaster/reports/`目录存储任务复杂性分析等报告。
   - `.cursor/rules/taskmaster.mdc`提供TaskMaster命令的详细参考。
   - `.cursor/rules/dev_workflow.mdc`描述使用TaskMaster的开发工作流程。

5. **测试相关**:
   - `test_html/auth_test.html`提供基于浏览器的认证测试界面，用于验证登录/登出/密码更改功能。
   - `test_html/permissions_test.html`提供角色权限测试界面，用于验证不同角色用户的权限控制和API访问限制。
   - `a7/users/tests.py`包含自动化单元测试，覆盖认证、权限和端到端用户场景测试。
   - `a7/courses/tests.py`包含课程模型的自动化测试，验证课程内容管理功能的正确性，以及练习题、学生答案和学习记录的功能测试，包括学习进度跟踪、状态转换和统计分析测试。
   - `a7/apps/core/tests.py`: 包含核心模型的自动化测试，验证用户活动跟踪和系统性能监控功能，测试JSON字段处理方法和真实应用场景模拟。
   - `a7/apps/core/tests/test_middleware.py`: 核心中间件测试文件，包含对RequestLoggingMiddleware和RequestProcessorMiddleware的单元测试，验证路径排除、日志记录、请求验证、响应处理和请求大小限制功能。
   - `test_api.py`: API测试脚本，用于集成测试中间件功能，包括JWT认证、请求日志和请求处理。提供实际HTTP请求测试，验证中间件在真实环境中的表现。
   - `marp_integration_test.py`: 手动集成测试脚本，用于测试知识点到PPT的完整流程，包括知识点数据准备、Markdown生成（支持本地和AI两种模式）、Markdown验证和修复、以及转换为演示文稿（支持pptx/pdf/html格式）。脚本设计为可通过命令行参数配置，提供详细的日志记录，并保存所有中间文件用于分析和调试。

6. **Cursor与TaskMaster集成**:
   - `.cursor/rules/`目录存储Cursor IDE使用的规则文件，包括:
     - `taskmaster.mdc`提供TaskMaster命令的详细参考和使用指南
     - `dev_workflow.mdc`描述使用TaskMaster的开发工作流程和最佳实践
     - `cursor_rules.mdc`定义规则文档的格式和要求
     - `self_improve.mdc`提供规则改进的指南和策略
     - `context7.mdc`和`file_structure.mdc`提供特定功能的规则支持
   - `.cursor/mcp.json`配置Model Control Protocol功能，实现TaskMaster工具的集成
   - `.roomodes`定义Roo助手的行为模式，确保与Cursor功能兼容
   - `.windsurfrules`配合IDE规则，定义项目的代码和文档生成规则
   - 这些配置协同工作，提供强大的辅助开发功能和遵循项目规范的自动化支持

7. **TaskMaster开发工作流**:
   - `.taskmaster/config.json`存储TaskMaster配置，包括AI模型、参数和用户偏好
   - `.taskmaster/tasks/tasks.json`维护所有任务的定义、状态和关系
   - `.taskmaster/tasks/task_*.txt`为每个任务提供详细描述、实现步骤和测试策略
   - `.taskmaster/reports/`存储复杂性分析等自动生成的报告，辅助任务分解
   - `.taskmaster/docs/prd.txt`存储项目需求文档，作为任务生成和规划的基础
   - 完整的任务生命周期管理：创建、分解、实现、测试和完成
   - 支持基于依赖的任务排序，确保按正确顺序处理任务
   - 通过`.cursor/rules/dev_workflow.mdc`详细说明的工作流程，指导开发者高效使用TaskMaster

8. **开发环境配置**:
   - `a7.code-workspace`定义VS Code的项目视图和配置
   - `requirements.txt`列出项目的Python依赖，供开发和部署环境使用
   - 各种日志文件(`permission.log`, `request.log`, `jwt_auth.log`)记录系统活动，辅助调试
   - `pytest.ini`配置测试框架，定义异步测试行为和自定义标记

9. **用户活动和性能监控系统**:
   - `a7/apps/core/models.py`定义UsageStatistics和PerformanceMetric模型，用于跟踪用户活动和系统性能。
   - `a7/apps/core/admin.py`配置这些模型在Django Admin中的展示和操作方式。
   - `a7/apps/core/tests.py`提供这些模型的自动化测试，验证其功能正确性。
   - UsageStatistics模型与User模型建立外键关系，跟踪特定用户的系统使用情况。
   - UsageStatistics和PerformanceMetric模型都使用JSON字段存储复杂的详细信息，并提供解析方法。

10. **学习进度跟踪系统**:
   - `a7/courses/models.py`中的LearningRecord模型用于跟踪学生的学习进度和时间投入。
   - LearningRecord模型通过外键关联User(student)、Course和KnowledgePoint模型，建立学生-课程-知识点的学习关系，使用CASCADE级联删除。
   - LearningRecord模型提供进度更新方法、时间累计方法和状态判断属性，实现完整的学习进度跟踪功能。
   - `a7/courses/admin.py`配置LearningRecord模型在Django Admin中的展示和操作方式。
   - `a7/courses/tests.py`提供学习记录模型的自动化测试，验证学习进度跟踪、状态转换和统计分析功能。
   - LearningRecord模型添加了lr_progress_idx等多个优化索引，提高查询性能。
   - 新增CourseProgress模型，通过外键关联User(student)和Course模型，跟踪学生整体课程进度。
   - CourseProgress模型提供overall_progress（总体进度）、required_completed（必修内容完成状态）、correctness_rate（正确率）和total_time_spent（总学习时间）字段，全面记录学习状态。
   - CourseProgress模型实现update_from_learning_records方法，自动从学习记录计算更新整体进度。
   - KnowledgePoint模型扩展is_required（是否必修）和estimated_time（预计学习时间）字段，支持必修内容跟踪和学习时间规划。
   - Exercise模型扩展is_required（是否必修）、correct_count（正确次数）和attempt_count（尝试次数）字段，支持必修练习跟踪和正确率统计。
   - Exercise模型提供correctness_rate属性，自动计算练习题的正确率。
   - StudentAnswer模型扩展is_correct（是否正确）和attempt_count（尝试次数）字段，记录答题正确性和尝试次数。
   - `a7/courses/serializers_progress.py`定义专门的进度跟踪序列化器，支持进度数据的API交互。
   - `a7/courses/tests/test_progress_models.py`和`a7/courses/tests/test_progress_serializers.py`提供全面的单元测试，验证进度跟踪功能的正确性和完整性。
   - `a7/courses/services/progress_tracker.py`实现ProgressTrackerService服务类，提供更新练习题统计信息、知识点进度和课程整体进度的方法，以及获取学生进度概览的功能。
   - `a7/courses/views.py`中的ProgressTrackingViewSet提供进度跟踪API端点，包括获取课程进度、知识点进度、更新学习记录和获取学生进度概览功能。
   - `a7/courses/tests/test_progress_tracking.py`提供进度跟踪API的单元测试，验证API端点功能和权限控制。
   - 实现了信号处理器，通过Django信号机制自动触发进度更新：当学生提交答案时更新相关进度，当学习记录更新时更新课程进度。
   - StudentAnswer模型增强了save方法，实现跟踪答案正确性变化，并自动更新相关统计数据。

11. **模型关系优化系统**:
    - 为所有模型添加了优化的索引设计，提高查询性能。
    - 实现了精心设计的外键关系级联删除策略：用户相关使用SET_NULL保护数据，内容关系使用CASCADE维持一致性。
    - 所有索引和外键关系均在迁移文件中正确定义，如`a7/courses/migrations/0004_rename_courses_lea_student_a74868_idx_lr_stud_course_idx_and_more.py`。
    - `a7/courses/tests.py`中的ComprehensiveModelRelationshipTest测试类验证所有模型关系、外键、反向查询和级联删除行为，包括教师删除对课程的影响、课程删除对知识点的级联删除等。

12. **REST Framework API系统**:
    - `a7/a7/settings.py`中的`REST_FRAMEWORK`配置已更新，`DEFAULT_AUTHENTICATION_CLASSES`添加了JWT认证，`DEFAULT_PERMISSION_CLASSES`仍设置为`AllowAny`，但视图可以覆盖此设置。
    - DRF配置与用户认证系统的集成已启用，API端点可通过权限类进行访问控制。
    - `a7/users/middleware/jwt_auth_middleware.py`在settings.py中已启用，对请求进行令牌验证。
    - `a7/apps/core/middleware/request_processor_middleware.py`确保API响应格式标准化，添加安全响应头，提高API交互的一致性和安全性。
    - `a7/apps/core/middleware/request_logging_middleware.py`记录API调用信息，为性能优化和问题诊断提供数据支持。
    - 分页配置确保大型数据集的高效处理，防止返回过多数据导致性能问题。
    - 渲染器配置支持多种格式输出，既可返回生产环境的JSON数据，也支持开发环境的可视化API界面。
    - 解析器配置支持多种输入格式，包括JSON数据、表单数据和文件上传。
    - 过滤和搜索配置为API提供强大的数据查询能力，支持高级搜索和结果排序。新增django-filter配置，为所有API端点提供统一的过滤功能支持。
    - 异常处理确保API错误以一致的格式返回，便于客户端处理。
    - 版本控制配置支持API演进和向后兼容性管理。
    - 格式配置优化响应大小和时间表示，提高API效率和可用性。
    - 测试配置简化API自动化测试开发。
    - `a7/users/views.py`中的API视图使用`swagger_auto_schema`装饰器和OpenAPI Schema定义API文档，避免直接使用未渲染的Response对象，确保Swagger文档正确生成。
    - API文档通过`drf-yasg`实现，提供Swagger UI和ReDoc两种交互式文档，帮助前端开发者了解API结构和使用方法。

13. **API监控与日志系统**:
    - `a7/apps/core/middleware/request_logging_middleware.py`实现API请求监控，记录请求方法、路径、状态码和处理时间。
    - `a7/users/middleware/jwt_auth_middleware.py`原本记录认证过程，但目前已禁用。
    - `request.log`存储API请求日志，提供系统调用情况的完整记录。
    - `jwt_auth.log`存储认证日志，记录用户认证活动，有助于安全审计和问题排查。
    - `a7/a7/settings.py`中的`LOGGING`配置定义了日志记录的格式、级别和目标，实现灵活的日志管理。
    - `REQUEST_LOG_EXCLUDE_PATHS`和`PROCESSOR_EXCLUDE_PATHS`配置排除某些路径，避免记录不必要的请求，提高系统效率。
    - `a7/apps/core/tests/test_middleware.py`验证日志记录功能的正确性和完整性。
    - 日志系统与性能监控系统(`PerformanceMetric`模型)协同工作，提供系统运行情况的全面视图。

14. **Docker部署系统**:
    - `a7/Dockerfile`定义应用容器构建过程，通过分层构建优化缓存和镜像大小。
    - `a7/compose.yaml`配置容器服务，定义网络设置、端口映射以及多容器协作方式。
    - `a7/README.Docker.md`提供Docker使用指南，包括本地开发和云部署说明。
    - `a7/.dockerignore`通过排除不必要文件优化构建过程和减小镜像体积。
    - `a7/a7/wsgi.py`作为Gunicorn的入口点，提供容器化部署时的WSGI服务器支持。
    - `requirements.txt`被Dockerfile使用，确保容器安装了所有依赖包。
    - Docker配置与Django设置协同工作，容器启动时使用`a7/a7/settings.py`中的配置。
    - Docker容器暴露的8000端口与Django开发服务器使用的端口一致，简化了开发到部署的过渡。
    - 容器使用非特权用户运行应用以增强安全性，遵循Docker最佳实践。
    - Docker环境变量（`PYTHONDONTWRITEBYTECODE`和`PYTHONUNBUFFERED`）优化了Python在容器环境中的运行。

15. **AI服务系统**:
    - `a7/ai_services/models.py`定义了webhook配置和调用日志的核心数据模型。
    - `a7/ai_services/services/n8n_webhook/client.py`实现异步HTTP客户端处理与n8n服务的通信，并集成验证逻辑。还提供问题生成的便捷方法（generate_questions和generate_questions_sync）以及学生对话的便捷方法（dialogue_with_student和dialogue_with_student_sync）。新增答案校正的便捷方法（correct_student_answer和correct_student_answer_sync），支持评估学生提交的答案并提供结构化的反馈。新增练习题生成的便捷方法（generate_exercises和generate_exercises_sync），支持根据查询文本和知识点内容生成练习题。
    - `a7/ai_services/services/n8n_webhook/exceptions.py`定义异常类型，统一错误处理机制。
    - `a7/ai_services/services/n8n_webhook/formats.py`使用Pydantic定义灵活的请求/响应数据模型，以适应外部服务的不同输出。包含问题生成相关的数据模型（QuestionGenerationRequestData、QuestionData、QuestionGenerationResponseData）和学生对话相关的数据模型（DialogueRequestData、DialogueResource、DialogueResponseData）。新增练习题生成相关的数据模型（ExerciseGenerationRequestData、ExerciseGenerationResponseData）和解析函数（parse_exercise_text、parse_single_exercise），支持从文本中提取练习题内容、选项和答案。题型格式使用下划线格式（如"single_choice"、"multiple_choice"），确保与系统其他部分的格式一致。新增答案校正相关的数据模型（AnswerCorrectionResponseData）和解析函数（format_answer_correction_response），支持从AI服务返回的文本中提取结构化的答案评估结果，包括正确性、得分、反馈、改进建议和解析说明。
    - `a7/ai_services/views.py`中的N8nWebhookAPIView权限类已设置为[AllowAny]，允许无需认证即可访问。新增StudentDialogueViewSet视图集，处理学生对话请求，权限设置为[AllowAny]，允许学生无需认证即可使用。新增ExerciseGenerationViewSet视图集，实现练习题生成API，允许匿名访问，支持根据查询文本、知识点ID、题型、数量和难度生成练习题，但不将生成的练习题保存到数据库。新增StudentAnswerCorrectionSerializer和StudentAnswerCorrectionViewSet，实现学生答案校正API，允许匿名访问，支持根据练习题ID和学生答案评估正确性并提供结构化反馈，包括正确性、得分、反馈意见、改进建议和解析说明。
    - `a7/ai_services/services/knowledge_converter.py`负责将AI服务（如n8n）返回的课程内容JSON数据，安全地转换为数据库中的Course和KnowledgePoint模型。包含对输入数据进行验证、处理层级结构（有深度限制以防无限递归）、以及在原子事务中完成数据库操作的健壮逻辑。
    - `a7/ai_services/services/question_export.py`提供导出工具，将问题数据转换为标准格式（JSON、CSV），支持文件命名和Unicode处理。
    - `a7/ai_services/urls.py`将API视图与URL路径映射，注册StudentDialogueViewSet提供'/api/student-dialogue/'端点。新增ExerciseGenerationViewSet注册，提供'/api/generate-exercises/'端点，用于练习题生成API。新增StudentAnswerCorrectionViewSet路由注册，提供'/api/correct-answer/'端点用于学生答案校正API。
    - `a7/courses/views.py`中的QuestionGenerationViewSet实现问题生成API端点，接收知识点ID、问题类型和数量等参数，调用n8n服务生成问题并返回标准化响应。
    - `a7/courses/serializers.py`中的QuestionGenerationSerializer负责问题生成API的请求参数验证。新增StudentDialogueSerializer负责学生对话API的请求参数验证。
    - `a7/courses/urls.py`注册QuestionGenerationViewSet，提供'/api/questions-generate/'端点。
    - `a7/courses/tests_api_questions.py`提供问题生成API的全面测试，验证功能完整性、参数验证和权限控制。
    - `a7/ai_services/tests/conftest.py`配置异步测试环境，提供共享事件循环和测试固件。
    - `a7/ai_services/api_response.py`提供标准化API响应的辅助函数。
    - `a7/ai_services/tests/test_student_dialogue.py`和`a7/ai_services/tests/test_student_dialogue_integration.py`提供学生对话API的单元测试和集成测试，验证功能完整性、错误处理和与真实n8n服务的集成。
    - `a7/ai_services/tests/test_exercise_generation.py`提供练习题生成API的单元测试，验证API端点功能、参数验证和错误处理，使用模拟技术测试API行为。
    - `a7/ai_services/tests/test_exercise_generation_integration.py`提供练习题生成API的集成测试，验证与真实N8N服务的交互测试，验证生成不同类型和难度的练习题。
    - `a7/ai_services/tests/test_answer_correction.py`提供学生答案校正API的单元测试，验证API端点功能、参数验证和错误处理。使用模拟（mock）技术测试API的行为，验证API能够正确处理请求、构造适当的prompt、调用AI服务并返回标准化响应。
    - `a7/ai_services/tests/test_answer_correction_integration.py`提供学生答案校正API的集成测试，包含与真实N8N服务的交互测试，验证API能够成功评估不同类型（单选题、多选题、简答题）的学生答案。测试包括正确答案和错误答案的评估，验证评分、反馈和建议的合理性。

16. **问题生成系统**:
    - `a7/ai_services/services/n8n_webhook/formats.py`中的QuestionData模型定义问题数据结构，支持多种题型（如简答题、选择题）和不同格式的答案模板（字符串或列表）。
    - `a7/ai_services/services/n8n_webhook/client.py`中的generate_questions和generate_questions_sync方法提供异步和同步的问题生成功能。
    - `a7/courses/serializers.py`中的QuestionGenerationSerializer验证问题生成请求参数，确保知识点ID、问题类型和数量等参数有效。
    - `a7/courses/views.py`中的QuestionGenerationViewSet处理问题生成API请求，调用n8n服务生成问题并返回标准化响应。扩展了export操作方法，支持以不同格式（JSON、CSV）导出生成的问题，实现会话存储机制。
    - `a7/courses/urls.py`注册'/api/questions-generate/'端点，提供RESTful API接口。
    - `a7/courses/tests_api_questions.py`包含全面的测试用例，验证问题生成API的功能完整性、参数验证和权限控制。
    - `a7/ai_services/services/question_export.py`提供导出工具，将问题数据转换为标准格式（JSON、CSV），支持文件命名和Unicode处理。
    - `a7/courses/tests/test_question_export.py`和`a7/courses/tests/test_question_export_integration.py`验证导出功能的正确性和稳定性。
    - 问题生成系统与知识点模型集成，基于知识点内容生成相关的教学练习题。
    - 支持多种问题类型（如简答题、选择题）和不同难度级别的问题生成。
    - 提供标准化的问题数据结构，包括标题、内容、类型、难度、答案模板和关联知识点ID。
    - 系统设计足够灵活，能够处理不同格式的答案模板（如简答题的文本答案和选择题的选项列表）。
    - 实现了完整的问题导出功能，支持JSON和CSV格式，满足不同场景下的数据交换需求。

17. **练习题和学生答案测试系统**:
    - `a7/courses/tests/test_api_exercises.py`提供练习题和学生答案API的基础CRUD功能测试，验证创建、读取、更新、删除操作，以及基本的过滤、排序和搜索功能。
    - `a7/courses/tests/test_api_exercises_additional.py`提供练习题和学生答案API的高级功能和边缘情况测试，包含5个专门的测试类：
      - ExerciseValidationTests：验证练习题字段（标题长度、类型有效性、必填字段）和边缘情况
      - StudentAnswerValidationTests：验证学生答案约束（唯一性约束、分数范围验证）
      - CombinedFilteringTests：测试组合过滤和排序测试，验证多条件筛选和多字段排序功能
      - PaginationAndEdgeCaseTests：测试分页功能、无效页码处理、特殊字符处理和超长内容处理
      - APIResponseFormatTests：验证API响应格式（列表、详情、错误响应、创建响应）
    - 这两个测试文件共同确保练习题和学生答案API在各种情况下都能正确处理请求并返回标准格式的响应，提高系统的稳定性和可靠性。
    - 测试覆盖了正常操作路径和异常情况，验证了API的健壮性和错误处理能力。
    - 测试还验证了API响应格式的一致性，确保前端应用能够依赖统一的数据结构。

18. **Marp演示文档转换服务**:
    - `a7/marp_service/__init__.py`提供顶层API接口convert_markdown_to_format和convert_file_to_format，作为与外部系统交互的主要入口点。包含对Windows环境的特殊处理，特别是PNG输出格式的处理。
    - `a7/marp_service/apps.py`: 应用配置文件，包含应用元数据和启动逻辑。
    - `a7/marp_service/cli.py`: Marp命令行接口构建与执行。MarpCLIBuilder类实现链式API设计，便于构建复杂的命令行参数。MarpCLIExecutor类负责执行构建好的命令行，包含对Windows环境的特殊处理，确保命令在不同操作系统上正确执行。使用简化的命令路径处理，直接使用"marp"命令或完整路径（如"npx @marp-team/marp-cli"），并在Windows环境下使用shell=True执行命令，解决了命令执行问题。
    - `a7/marp_service/exceptions.py`: 异常类定义，定义异常层次结构，通过继承关系组织不同类型的错误，使错误处理更加精确。
    - `a7/marp_service/temp.py`: 临时文件管理，MarpTempFileManager类提供上下文管理器接口，确保临时文件的生命周期管理，避免资源泄露。
    - `a7/marp_service/utils.py`: 工具函数，提供实用函数，支持格式验证和MIME类型映射，与`cli.py`和顶层API密切协作，确保输入输出的一致性。
    - `a7/marp_service/validation.py`: Markdown验证模块，实现MarkdownValidator类，提供五个核心功能：validate_frontmatter（验证前置元数据）、validate_slides_structure（验证幻灯片结构）、validate_hierarchy（验证标题层级）、validate_syntax（验证语法如代码块闭合）和fix（自动修复问题）。能够识别和修复常见问题如缺失的主题设置、标题层级跳跃和未闭合代码块等。
    - `a7/marp_service/serializers.py`: REST API序列化器，定义MarpConversionSerializer类处理输入验证，验证markdown内容、输出格式(pdf/pptx/html/png)和可选的主题，确保API请求数据的有效性。
    - `a7/marp_service/views.py`: REST API视图，实现MarpConversionView类处理HTTP请求，接收POST请求到/api/marp/convert端点，调用marp服务执行转换，并返回转换后的文件作为HTTP响应，带有适当的MIME类型。
    - `a7/marp_service/urls.py`: URL路由配置，定义API端点路径，将/api/marp/convert路径映射到MarpConversionView，并集成到主URL配置中。
    - `a7/marp_service/tests/test_cli.py`: CLI相关单元测试，验证命令行参数构建和执行功能。
    - `a7/marp_service/tests/test_exceptions.py`: 异常相关单元测试，验证异常类的行为和继承关系。
    - `a7/marp_service/tests/test_integration.py`: 集成测试，使用真实的marp-cli工具验证完整的转换流程。包含对不同输出格式（PDF、PPTX、HTML、PNG）的测试，以及对Windows和Linux/Mac环境的特殊处理，确保跨平台兼容性。使用@unittest.skipIf装饰器在不同环境下智能跳过特定测试。新增了check_marp_cli_available函数，简化了marp命令检测逻辑，适配Windows环境下的命令执行方式。
    - `a7/marp_service/tests/test_temp.py`: 临时文件管理单元测试，验证临时文件的创建、使用和清理。
    - `a7/marp_service/tests/test_utils.py`: 工具函数单元测试，验证格式验证和MIME类型映射功能。
    - `a7/marp_service/tests/test_serializers.py`: 序列化器单元测试，验证输入验证逻辑，包括格式验证、必填字段检查和主题验证。
    - `a7/marp_service/tests/test_views.py`: 视图单元测试，使用mock服务测试视图逻辑，验证请求处理、响应生成和错误处理。
    - `a7/marp_service/tests/test_simple.py`: 简单测试脚本，用于在Django测试环境之外直接测试marp命令的执行，验证不同调用方式（直接命令、完整路径、npx调用）在不同环境下的可行性。
    - `a7/a7/settings.py`中添加了MARP_CLI_PATH配置项，用于指定marp-cli的安装路径，支持系统级别的灵活配置。已更新为使用"marp"或"npx @marp-team/marp-cli"作为默认值，提高跨平台兼容性。
    - 测试文件(`test_cli.py`, `test_exceptions.py`, `test_integration.py`, `test_temp.py`, `test_utils.py`, `test_serializers.py`, `test_views.py`)分别验证各模块的功能和边界情况，确保服务的稳定性和可靠性。
    - `test_integration.py`实现了使用真实marp-cli工具的集成测试，验证不同输出格式（PDF、PPTX、HTML、PNG）的转换功能，并通过平台检测和条件测试跳过确保在Windows和Linux/Mac环境下都能正确运行。
    - 该服务设计为可独立使用的Django应用，通过INSTALLED_APPS注册，可以方便地集成到a7项目或其他Django项目中。
    - 服务实现了Markdown转换为PDF、PPTX、HTML和PNG等常见演示文档格式，支持自定义主题、背景色、页面比例等参数。
    - 服务具有跨平台兼容性，通过特殊处理确保在Windows和Linux/Mac环境下都能正确工作，特别是处理了Windows环境下的命令执行和PNG输出格式的特殊需求。Windows环境下使用shell=True执行命令，解决了命令路径解析问题。
    - REST API端点(/api/marp/convert)提供了完整的Markdown到演示文档的转换功能，支持多种输出格式和主题选项，返回适当的MIME类型和文件名，集成了Swagger文档，便于API使用者理解和调用。

19. **知识点到PPT转换系统**:
   - `a7/courses/serializers_ppt.py`定义KnowledgePointToPPTSerializer类，验证知识点转PPT的输入参数。新增direct_download和filename参数，支持直接下载功能，使API能够根据客户端需求返回文件内容或文件URL。
   - `a7/courses/services/knowledge_to_ppt.py`实现KnowledgePointToPPTService类，提供知识点层次结构获取、Markdown生成和文件转换功能。集成了MarkdownValidator进行内容验证和修复，确保生成的Markdown符合marp规范。
   - `a7/courses/views.py`中的KnowledgePointToPPTViewSet处理API请求，验证输入并调用服务完成转换。增强了响应处理，支持基于direct_download参数的响应模式选择：当设置为true时，将文件直接作为响应返回，带有适当的Content-Type和Content-Disposition头信息；否则返回文件URL或Base64编码的文件内容。
   - `a7/courses/urls.py`注册KnowledgePointToPPTViewSet，提供'/api/knowledge-points-to-ppt/'端点。
   - `a7/courses/tests/test_knowledge_to_ppt_api.py`和`a7/courses/tests/test_knowledge_to_ppt_real.py`验证API功能和实际文件生成。
   - `a7/courses/tests/test_knowledge_to_ppt_conversion.py`提供针对validate_and_convert_markdown方法的单元测试，验证Markdown验证、修复和转换功能，包括有效内容处理、无效内容修复、不同输出格式、主题和异常处理等测试场景。
   - `a7/courses/tests/test_knowledge_to_ppt_integration.py`提供完整流程的集成测试，从知识点数据准备到最终PPT生成的全流程测试，确保各组件协同工作正常。
   - `a7/run_markdown_to_ppt_tests.py`用于自动化执行知识点到PPT转换相关的测试套件，提供集中式测试执行和结果分析。
   - `marp_integration_test.py`提供完整的集成测试脚本，可手动执行测试知识点到PPT的整个流程，包括使用真实的n8n服务进行Markdown生成、验证和修复、以及转换为演示文稿。支持--use-ai参数切换AI生成和本地生成模式，支持多种输出格式(pptx/pdf/html)，提供详细的日志记录。
   - `a7/marp_service/__init__.py`提供convert_markdown_to_format方法，由KnowledgePointToPPTService调用以将Markdown转换为演示文稿。
   - `a7/marp_service/cli.py`提供MarpCLIBuilder和MarpCLIExecutor类，负责构建和执行marp-cli命令，实现Markdown到演示文稿的转换功能。
   - `a7/marp_service/validation.py`提供MarkdownValidator类，对Markdown内容进行验证和自动修复，确保符合marp规范和保持知识点层级结构。
   - 转换服务生成的文件保存在presentations/目录（临时文件）或复制到pptx_output/目录（用于长期保存和查看）。
   - 系统支持多种输出格式（pptx、pdf、html），并能够保留知识点的层级结构，反映在生成的演示文稿中。
   - 服务实现了错误处理，包括知识点ID不存在、转换失败等情况的适当响应。
   - KnowledgePointToPPTService实现了完整的处理流程，将课程管理系统与Marp服务无缝集成，实现从结构化知识点数据到完整演示文稿的转换。
   - 系统具有高度的健壮性，能够处理各种边缘情况，如MEDIA_ROOT或MEDIA_URL为None的情况，确保在不同环境下都能正常工作。
   - 实现了详细的测试套件，包括单元测试和集成测试，覆盖各种正常和异常场景，确保功能的稳定性和可靠性。
   - 提供了三种视觉主题样式（默认主题、教学主题、极简主题），每种主题都有多种颜色方案选项（如绿色、紫色等）。
   - 视觉增强功能通过样式设计反映知识点的层次结构：父知识点使用更大、更突出的标题样式，子知识点使用缩进和不同的视觉样式，通过颜色编码增强层次关系的视觉表现。
   - `a7/courses/tests/test_knowledge_to_ppt_direct_download.py`提供直接下载功能的专门测试，验证Content-Type设置、Content-Disposition头信息和文件内容的正确性。
   - `test_html/ppt_direct_download_test.html`前端测试页面，提供浏览器环境下的直接下载功能测试界面。
   - `api_test_runner.py`端到端测试脚本，提供自动化测试流程，验证直接下载功能在不同格式(PPTX/PDF/HTML)下的正确性和性能表现。
   - 系统支持根据客户端需求选择两种不同的响应模式：直接下载（适合浏览器端使用）和文件URL/Base64内容返回（适合程序化调用）。
   - 直接下载功能在性能测试中表现良好，PPTX格式初始生成约需30秒，而PDF和HTML格式通常在2秒内完成，文件大小分别约为560KB(PPTX)、150KB(PDF)和106KB(HTML)。

20. **学生助手对话系统**:
    - `a7/ai_services/views.py`中的StudentDialogueViewSet视图集处理学生对话请求，提供API端点接收学生查询并返回AI助手回答。
    - `a7/ai_services/services/n8n_webhook/client.py`中的dialogue_with_student和dialogue_with_student_sync方法提供异步和同步的学生对话功能。
    - `a7/ai_services/services/n8n_webhook/formats.py`中的DialogueRequestData和DialogueResponseData模型定义学生对话的请求和响应数据结构，支持会话ID跟踪多轮对话。
    - `a7/courses/serializers.py`中的StudentDialogueSerializer验证学生对话请求参数，确保查询文本有效。
    - `a7/ai_services/urls.py`注册StudentDialogueViewSet，提供'/api/student-dialogue/'端点，实现RESTful API接口。
    - `a7/ai_services/tests/test_student_dialogue.py`包含全面的单元测试用例，验证学生对话API的功能完整性、参数验证和错误处理。
    - `a7/ai_services/tests/test_student_dialogue_integration.py`提供与真实n8n服务的集成测试，验证单轮对话和多轮对话功能。
    - 学生对话系统与n8n服务集成，通过AI模型提供智能回答，支持教育场景中的学生辅助功能。
    - 系统设计支持多轮对话，通过会话ID跟踪对话上下文，提供连贯的交互体验。
    - 响应数据结构包含主要答案、相关资源和后续问题建议，丰富学生的学习体验。
    - 系统实现了完整的错误处理机制，包括参数验证错误、n8n服务错误和一般异常处理。
    - API端点设置为允许匿名访问，便于学生无需认证即可使用对话功能。
    - 使用标准化的API响应格式，确保前端应用能够依赖统一的数据结构。

21. **练习题生成系统**:
    - `a7/ai_services/services/n8n_webhook/formats.py`中的练习题生成相关数据模型（ExerciseGenerationRequestData、ExerciseGenerationResponseData）定义练习题生成的请求和响应结构，确保数据一致性。
    - `a7/ai_services/services/n8n_webhook/formats.py`中的解析函数（parse_exercise_text、parse_single_exercise）实现从文本中提取练习题内容、选项和答案的功能，支持不同格式的练习题文本解析。
    - `a7/ai_services/services/n8n_webhook/formats.py`中的题型格式统一使用下划线格式（如"single_choice"、"multiple_choice"），确保与系统其他部分的格式一致，避免因格式不匹配导致的错误。
    - `a7/ai_services/services/n8n_webhook/client.py`中的generate_exercises和generate_exercises_sync方法提供异步和同步的练习题生成功能，支持根据查询文本和知识点内容生成练习题。
    - `a7/ai_services/views.py`中的ExerciseGenerationSerializer验证练习题生成请求参数，确保查询文本、知识点ID、题型、数量和难度等参数有效。
    - `a7/ai_services/views.py`中的ExerciseGenerationViewSet处理练习题生成API请求，调用n8n服务生成练习题并返回标准化响应，支持匿名访问，便于学生使用。
    - `a7/ai_services/urls.py`注册'/api/generate-exercises/'端点，提供RESTful API接口。
    - `a7/ai_services/tests/test_exercise_generation.py`包含全面的单元测试用例，验证练习题生成API的功能完整性、参数验证和错误处理。
    - `a7/ai_services/tests/test_exercise_generation_integration.py`提供与真实N8N服务的集成测试，验证练习题生成API的端到端功能。
    - 练习题生成系统与知识点模型集成，基于知识点内容生成相关的教学练习题。
    - 支持多种题型（如单选题、多选题、简答题）和不同难度级别的练习题生成。
    - 提供标准化的练习题数据结构，包括标题、内容、类型、难度、答案模板等。
    - 系统设计足够灵活，能够处理不同格式的答案模板（如简答题的文本答案和选择题的选项列表）。
    - 练习题生成API不保存生成的练习题到数据库，而是直接返回给客户端，适合用于学生自主练习和临时题目生成场景。

22. **学生答案校正系统**:
    - `a7/ai_services/services/n8n_webhook/formats.py`中的AnswerCorrectionResponseData模型定义答案校正的响应数据结构，包含正确性评估、得分、反馈、改进建议和解析说明等字段。
    - `a7/ai_services/services/n8n_webhook/formats.py`中的format_answer_correction_response函数负责从AI服务返回的文本中提取结构化的答案评估结果，实现健壮的文本解析和JSON提取逻辑。
    - `a7/ai_services/services/n8n_webhook/client.py`中的correct_student_answer和correct_student_answer_sync方法提供异步和同步的答案校正功能，支持评估学生提交的答案并提供结构化的反馈。
    - `a7/ai_services/views.py`中的StudentAnswerCorrectionSerializer验证答案校正请求参数，确保练习题ID和学生答案内容有效，并验证练习题是否存在。
    - `a7/ai_services/views.py`中的StudentAnswerCorrectionViewSet处理答案校正API请求，根据练习题类型构建适当的评估prompt，调用n8n服务评估学生答案并返回结构化反馈，支持匿名访问，便于学生使用。
    - `a7/ai_services/urls.py`注册'/api/correct-answer/'端点，提供RESTful API接口。
    - `a7/ai_services/tests/test_answer_correction.py`包含单元测试用例，验证答案校正API的功能完整性、参数验证和错误处理，使用模拟技术测试API行为。
    - `a7/ai_services/tests/test_answer_correction_integration.py`提供与真实N8N服务的集成测试，验证答案校正API能够成功评估不同类型（单选题、多选题、简答题）的学生答案。
    - 答案校正系统与练习题模型集成，基于练习题内容和答案模板评估学生答案的正确性。
    - 支持多种题型的答案评估，包括单选题、多选题和简答题，并针对不同题型提供特定的评分标准和反馈。
    - 系统设计采用结构化prompt模板，包含练习题详情、选项信息、学生答案和评估指示，确保AI能够准确理解任务和数据。
    - 对于多选题，系统提供特定的评分标准，根据选择的正确选项比例给出合理的得分。
    - 响应数据结构包含正确性评估（布尔值）、得分（0-100分）、详细反馈、改进建议和解题思路/解析，为学生提供全面的学习支持。
    - API端点设置为允许匿名访问，便于学生无需认证即可使用答案校正功能。
    - 系统不直接保存评估结果到数据库，而是实时返回给客户端，适合用于学生自主学习和即时反馈场景。

## 目录组织逻辑

项目采用了以下组织逻辑：

1. **Django项目结构**:
   - 遵循Django标准项目结构，核心配置放在内部a7包中。
   - Django应用存放在apps目录下，如core应用。
   - 用户管理系统作为独立应用(users)实现，便于模块化管理。
   - 课程管理系统作为独立应用(courses)实现，集中管理课程相关功能。
   - Marp服务作为独立应用(marp_service)实现，专注于Markdown到演示文档的转换功能。
   - AI服务应用(ai_services)提供与外部AI服务集成的功能。
   - 每个应用都有自己的URLs和视图模块。

2. **按工具分类**: 
   - 每个主要工具(TaskMaster, Cursor)都有其专用配置文件和目录。
   - TaskMaster相关文件集中在.taskmaster目录，遵循其标准结构。
   - Cursor配置和规则存放在.cursor目录，包含MCP配置和规则文件。

3. **按功能分类**:
   - `.cursor/rules/`中的规则按功能领域组织，提供开发指南和最佳实践。
   - `.taskmaster/`目录包含任务管理、PRD文档和报告等。
   - `a7/apps/`、`a7/users/`、`a7/courses/`和`a7/ai_services/`目录按功能划分不同的Django应用。
   - `test_html/`目录包含前端测试文件，按功能分类。
   - `api_test_output/`和`marp_test_output/`分别存储API测试和Marp测试的输出文件。
   - `pptx_output/`专门用于存储生成的演示文稿文件。

4. **配置与内容分离**:
   - 配置文件(如`.taskmaster/config.json`, `.roomodes`, `.cursor/mcp.json`)分布在各自的目录中。
   - 实际内容(如规则文件、任务文件、生成的PPTX)存储在相关子目录中。
   - 生成的PPTX文件存储在`pptx_output/`目录和`a7/presentations/`目录，便于浏览和分享。
   - 日志文件(`permission.log`, `request.log`, `jwt_auth.log`)放在根目录，便于快速访问和检查。

5. **测试与实现分离**:
   - 单元测试放在各应用目录的tests子目录中(`a7/users/tests/`, `a7/courses/tests/`, `a7/ai_services/tests/`)
   - 手动/前端测试文件放在单独的`test_html/`目录下
   - 集成测试脚本(`marp_integration_test.py`, `api_test_runner.py`)放在根目录
   - 测试输出文件存放在专门的目录(`api_test_output/`, `marp_test_output/`)

## 命名约定

1. **目录命名**:
   - 以功能或工具名称作为前缀，如`rules-architect/`表示架构相关规则。
   - 使用小写字母和连字符(-)分隔单词，如`rules-debug/`。
   - Django应用目录使用全小写字母，单数形式命名，如`core/`、`users/`、`courses/`。

2. **配置文件命名**:
   - 以点(.)开头的隐藏文件夹用于配置和工具，如`.taskmaster/`、`.cursor/`、`.github/`。
   - 配置文件通常以JSON格式存储，如`config.json`、`mcp.json`，便于程序解析。
   - 采用全小写字母，使用描述性名称。
   - Docker相关配置文件遵循行业标准命名，如`Dockerfile`（首字母大写，无扩展名）和`compose.yaml`（全小写）。

3. **文档文件命名**:
   - Markdown文档使用描述性名称，如`fileStructure.md`、`CurrentPlan.md`、`context7_library.md`。
   - 特定工具的规则文档使用`.mdc`扩展名，如`taskmaster.mdc`、`dev_workflow.mdc`。
   - 使用描述性名称，清晰表达文件内容。
   - 特定工具或技术的README文件使用`.工具名.md`格式，如`README.Docker.md`。

4. **代码约定**:
   - 代码文件（当添加时）将遵循各语言的标准命名约定。
   - 组件和模块文件名应反映其功能和类型。
   - Django模型类使用单数名词，首字母大写的驼峰式命名(如`User`、`Role`、`Course`、`KnowledgePoint`、`Exercise`、`StudentAnswer`)。
   - Django视图函数使用小写下划线命名(如`user_login`)。
   - Django URL路径使用小写和连字符分隔(如`user-profile/`)。

## API结构

项目已配置以下API结构：

1. **REST Framework全局配置**:
   - **认证配置**: 使用会话认证（支持API浏览器）和JWT令牌认证（已启用）
   - **权限配置**: 默认设置为AllowAny，但各视图可设置更严格的权限要求
   - **分页配置**: 使用页码分页，默认每页20条数据
   - **渲染器配置**: 支持JSON和可浏览API格式输出
   - **解析器配置**: 支持JSON、表单数据和多部分表单数据（含文件上传）输入
   - **异常处理**: 使用默认异常处理器处理API错误
   - **过滤配置**: 支持搜索过滤和结果排序，配置了DjangoFilterBackend作为默认过滤后端
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
   - `/swagger/` - Swagger UI API交互式文档，使用OpenAPI Schema定义响应格式
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
   - `/api/course-generate/` - 使用AI生成课程内容的端点
   - `/api/exercises/` - 练习题列表和创建（支持按知识点、题型和难度过滤，按创建时间、难度等排序，按标题和内容搜索）
   - `/api/exercises/<id>/` - 练习题详情、更新和删除
   - `/api/student-answers/` - 学生答案列表和创建（支持按学生、练习题和得分过滤，按提交时间和得分排序，按答案文本搜索）
   - `/api/student-answers/<id>/` - 学生答案详情、更新和删除
   - 所有端点实现权限控制（当前大部分已放开），确保数据一致性、有效性和适当的错误处理
   - 所有端点返回标准化的响应格式，包含状态码、成功标志和数据

7. **AI服务API**:
   - `/api/ai/webhook/` - n8n Webhook API端点，接收并处理AI任务请求
   - `/api/questions-generate/` - 问题生成API端点，接收知识点ID、问题类型和数量等参数，返回AI生成的格式化问题
   - `/api/questions-generate/export/` - 问题导出API端点，支持将生成的问题导出为JSON或CSV格式
   - `/api/student-dialogue/` - 学生助手对话端点，接收学生查询并返回AI助手回答
   - `/api/generate-exercises/` - 练习题生成API端点，接收查询文本、知识点ID、题型、数量和难度等参数，返回AI生成的练习题
   - `/api/correct-answer/` - 学生答案校正API端点，接收练习题ID和学生答案，返回评估结果（正确性、得分、反馈、改进建议和解析）
   - 支持POST方法，接收任务类型、任务数据和webhook配置ID
   - 需要认证（JWT令牌）访问
   - 支持不同任务类型，如"ragAI"（检索增强生成式AI）、"questionGeneration"（问题生成）和"exerciseGeneration"（练习题生成）
   - 处理请求数据验证、webhook配置查找和任务处理
   - 返回标准化的API响应（成功或错误信息）
   - 提供丰富的错误处理（请求错误、连接错误、超时错误）
   - 与n8n工作流自动化工具集成，支持AI任务处理
   - 练习题生成API允许匿名访问，便于学生使用，不将生成的练习题保存到数据库

8. **Marp服务API**:
   - `/api/marp/convert` - Markdown转换API端点，接收POST请求，包含markdown内容、输出格式和可选主题
   - 支持多种输出格式：PDF、PPTX、HTML、PNG
   - 返回转换后的文件作为HTTP响应，带有适当的MIME类型和文件名
   - 提供详细的错误处理，包括格式验证、转换错误和服务器错误
   - 集成Swagger文档，提供API使用说明和示例

9. **学习进度跟踪API**:
   - `/api/progress/course-progress/<course_id>/` - 获取指定课程的学习进度详情，支持教师查看任意学生进度，学生只能查看自己的进度
   - `/api/progress/knowledge-point-progress/<kp_id>/` - 获取指定知识点的学习进度，包括完成状态、进度百分比和学习时间
   - `/api/progress/update-learning-record/` - 更新学习记录，支持更新进度值、累加学习时间和更改状态
   - `/api/progress/student-summary/` - 获取学生进度概览，包括所有课程或指定课程的进度统计
   - `/api/progress/batch-knowledge-point-progress/` - 批量获取多个知识点的学习进度，提高前端性能
   - `/api/progress/exercise-statistics/` - 获取练习题完成情况和统计信息，支持按课程或知识点筛选，可选包含详细的练习题答题情况
   - 所有进度跟踪API均实现了权限控制，确保学生只能访问自己的进度数据
   - 进度数据自动计算和更新，支持实时反映学生的学习状态
   - 提供全面的统计信息，包括完成率、正确率、学习时间和最后活动时间
   - 支持必修内容完成状态跟踪，区分必修和选修内容的完成情况

10. **知识点到PPT转换API**:
   - `/api/knowledge-points-to-ppt/` - 知识点转PPT演示文稿端点，接收知识点ID列表并返回演示文稿（支持URL或Base64编码的文件内容）

11. **学生助手对话API**:
   - `/api/student-dialogue/` - 学生助手对话端点，接收学生查询并返回AI助手回答
   - 支持POST方法，接收查询文本、会话ID和可选上下文
   - 不需要认证（AllowAny权限类），允许学生无需登录即可使用
   - 支持多轮对话，通过会话ID跟踪对话上下文
   - 返回标准化的API响应，包含答案、相关资源和后续问题建议
   - 提供丰富的错误处理，包括参数验证错误、n8n服务错误和一般异常处理
   - 与n8n工作流自动化工具集成，支持AI模型驱动的智能回答
   - 响应包含会话ID，便于客户端进行后续对话

## 练习与评测系统

新增的Exercise和StudentAnswer模型为系统提供以下功能支持：

1. **练习题管理**:
   - 支持多种题型：单选题、多选题、填空题、简答题、编程题等
   - 可设置难度等级（1-5级）
   - 与知识点关联，实现按知识点组织练习题
   - 支持答案模板，用于标准答案或选项设置
   - 新增is_required字段，标记必修练习题
   - 新增correct_count和attempt_count字段，自动统计答题情况
   - 提供correctness_rate属性，自动计算正确率

2. **学生答案管理**:
   - 记录学生提交的答案内容
   - 支持评分和反馈记录
   - 确保每个学生对每道题只有一个有效答案
   - 记录提交时间，支持时间排序
   - 新增is_correct字段，标记答案正确性
   - 新增attempt_count字段，记录尝试次数
   - 自动更新相关练习题的统计数据

3. **学习进度跟踪**:
   - CourseProgress模型跟踪学生整体课程进度
   - 记录总体进度、必修内容完成状态、正确率和总学习时间
   - 自动从学习记录计算更新整体进度
   - 提供is_completed属性，判断课程是否完成
   - 记录completion_date，标记完成时间
   - 支持进度数据的API交互，便于前端展示

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

## 学习进度跟踪API

学习进度跟踪API提供了一套完整的端点，用于管理和查询学生的学习进度数据。

### 主要API端点

1. **课程进度查询 (`/api/progress/course-progress/<course_id>/`)**:
   - 获取指定课程的整体学习进度
   - 返回数据包括：整体完成百分比、必修内容完成状态、正确率、总学习时间、最后活动时间
   - 支持通过student_id参数查询特定学生的进度（教师/管理员权限）
   - 如果进度记录不存在，自动创建新记录

2. **知识点进度查询 (`/api/progress/knowledge-point-progress/<kp_id>/`)**:
   - 获取指定知识点的学习进度详情
   - 返回数据包括：完成状态、进度百分比、学习时间、最后访问时间
   - 支持通过student_id参数查询特定学生的进度（教师/管理员权限）
   - 使用select_related优化数据库查询，减少额外查询次数
   - 如果进度记录不存在，自动创建新记录

3. **学习记录更新 (`/api/progress/update-learning-record/`)**:
   - 更新学生的学习记录数据
   - 支持更新三种数据：进度值(0-100)、学习时间(分钟)和学习状态
   - 学习时间采用累加方式，而不是覆盖
   - 支持的状态值包括：'not_started', 'in_progress', 'completed', 'review_needed'
   - 包含完整的数据验证，确保输入数据有效

4. **学生进度概览 (`/api/progress/student-summary/`)**:
   - 获取学生的整体学习进度概览
   - 返回数据包括：所有课程的进度列表、已完成课程数量、平均正确率、总学习时间
   - 每个课程的数据包含：标题、整体进度、完成状态、正确率、学习时间
   - 支持通过course_id参数筛选特定课程的数据
   - 支持通过student_id参数查询特定学生的数据（教师/管理员权限）

5. **批量知识点进度查询 (`/api/progress/batch-knowledge-point-progress/`)**:
   - 同时获取多个知识点的学习进度数据
   - 通过ids参数指定要查询的知识点ID列表（逗号分隔）
   - 支持通过student_id参数查询特定学生的进度（教师/管理员权限）
   - 如果某些知识点不存在，返回not_found_ids列表
   - 针对前端性能优化，减少多次API调用

6. **练习题统计信息 (`/api/progress/exercise-statistics/`)**:
   - 获取练习题完成情况和统计数据
   - 支持按课程(course_id)或知识点(knowledge_point_id)筛选
   - 返回数据包括：总练习题数量、已完成数量、完成率、正确率、必修题完成情况、平均难度
   - 通过include_details参数可选择是否包含详细的练习题答题情况
   - 详情数据包含每道题的完成状态、正确性、得分、尝试次数等
   - 支持通过student_id参数查询特定学生的数据（教师/管理员权限）

### 权限控制

所有进度跟踪API都实现了严格的权限控制：

- 学生只能查看和更新自己的进度数据
- 教师和管理员可以查看任意学生的进度数据
- 权限检查通过_is_teacher_or_admin方法实现，支持多种判断方式：
  - 用户角色检查（role字段）
  - 用户名检查（针对预设账户和测试用例）
  - 权限检查（Django权限系统）
  - 用户组检查（Teachers和Administrators组）

### 数据模型集成

进度跟踪API与以下数据模型紧密集成：

- CourseProgress：存储课程整体进度数据
- LearningRecord：存储知识点级别的学习记录
- Exercise：包含练习题统计数据（尝试次数、正确次数、正确率）
- StudentAnswer：记录学生答案和评分数据

这些API端点共同提供了完整的学习进度跟踪功能，支持实时监控学生学习状态、评估学习效果和提供个性化学习体验。 