# 实现API端点和输入处理计划（任务20.2）

## 1. 需求分析

根据任务20.2的要求，需要实现三个API端点的后端逻辑，包括请求解析、验证和为n8n工作流调用准备数据：
- `/api/generate/teaching-outline/` - 生成教学大纲
- `/api/generate/exam-outline/` - 生成考试大纲
- `/api/generate/lesson-plan/` - 生成教案

这些端点已经在任务20.1中通过序列化器和视图集进行了设计，现在需要实现具体的请求处理和验证逻辑。

## 2. 现有代码分析

从文件结构和代码分析中，我发现：
1. 已有完整的API接口和URL配置：
   - 已在`urls.py`中注册路由
   - API基础路径：`/api/ai/generate/`
   - 视图集已定义：`TeachingOutlineViewSet`、`ExamOutlineViewSet`、`LessonPlanViewSet`

2. 已有请求/响应数据模型和格式化函数：
   - 请求模型：`KnowledgePointProcessingRequestData`
   - 响应模型：`KnowledgePointProcessingResponseData` 
   - 格式化函数：`format_teaching_outline_response`、`format_exam_outline_response`、`format_lesson_plan_response`

3. 已有客户端调用功能：
   - `N8nWebhookClient`类在`client.py`中已实现
   - 但需要实现具体的处理方法

## 3. 具体实现计划

1. **完善N8nWebhookClient类**：
   - 实现`generate_teaching_outline`、`generate_exam_outline`、`generate_lesson_plan`方法
   - 每个方法应包括同步和异步版本
   - 应处理请求数据验证和响应格式化

2. **完善API视图集**：
   - 完成`TeachingOutlineViewSet`、`ExamOutlineViewSet`和`LessonPlanViewSet`的`create`方法实现
   - 确保请求参数验证逻辑
   - 完善错误处理机制
   - 实现响应数据格式化

3. **添加输入验证和转换逻辑**：
   - 验证知识点数据结构
   - 转换输入数据为n8n工作流期望的格式
   - 确保在API层面进行必要的数据清理和格式化

## 4. 测试计划

1. **单元测试**：
   - 测试序列化器验证逻辑
   - 测试客户端方法的请求数据处理
   - 测试响应格式化函数

2. **集成测试**：
   - 测试端点调用与n8n工作流的集成
   - 测试成功和错误场景下的API响应
   - 测试不同知识点数据结构的处理

## 5. 实现步骤

1. 在`client.py`中实现必要的客户端方法
2. 完善视图集的`create`方法实现
3. 添加详细错误处理
4. 实现输入验证和转换逻辑
5. 编写测试用例

## 6. 注意事项

1. 确保API响应格式与系统标准一致
2. 处理会话ID，确保多轮对话能够正确跟踪
3. 实现错误记录，便于调试和监控
4. 遵循已有代码风格和架构模式
5. 确保权限控制正确设置（已在视图集中通过`permission_classes`设置）

