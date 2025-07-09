# 任务16.2: 集成AI用于Markdown生成

## 任务概述
利用现有AI服务将结构化知识点转换为Markdown内容，保持层级结构并符合marp-cli语法要求。

## 需求分析
1. 需要利用任务13中的AI服务 (n8n_webhook) 来生成Markdown
2. 确保生成的Markdown格式符合marp-cli语法要求
3. 保持原始知识点的层级结构
4. 解决字符串与数据结构之间的转换问题
5. 确保Markdown能被marp服务正确处理

## 技术依赖
1. 已有的n8n_webhook客户端 (`ai_services/services/n8n_webhook/client.py`)
2. 已有的marp服务 (`marp_service`)
3. 已有的知识点数据结构 (`courses/models.py`中的KnowledgePoint模型)
4. 已完成的知识点到PPT转换服务 (`courses/services/knowledge_to_ppt.py`)

## 实现方案

### 1. 创建Markdown生成服务
需要创建一个新的AI服务方法，专门用于知识点到Markdown的转换。

我们将扩展现有的n8n_webhook客户端，添加专门的方法来处理知识点到Markdown的转换请求：

- 在`ai_services/services/n8n_webhook/formats.py`中定义新的数据模型：
  - `KnowledgeToMarkdownRequestData`: 知识点到Markdown的请求数据模型
  - `KnowledgeToMarkdownResponseData`: 知识点到Markdown的响应数据模型

- 在`ai_services/services/n8n_webhook/client.py`中添加新方法：
  - `async generate_markdown_from_knowledge(self, request_data: Dict[str, Any]) -> Dict[str, Any]`
  - `def generate_markdown_from_knowledge_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]`

### 2. 扩展知识点到PPT转换服务
需要修改`courses/services/knowledge_to_ppt.py`中的`KnowledgePointToPPTService`类：

1. 重构当前的Markdown生成逻辑，分离为两个部分：
   - `generate_markdown_from_knowledge_points`: 使用本地逻辑生成Markdown（保留现有功能）
   - `generate_markdown_using_ai`: 调用AI服务生成Markdown（新增功能）

2. 修改`process_knowledge_points_to_ppt`方法，增加AI模式选择：
   - 增加参数`use_ai: bool = False`
   - 根据参数决定使用本地逻辑还是AI服务生成Markdown

### 3. 更新序列化器
修改`courses/serializers_ppt.py`中的`KnowledgePointToPPTSerializer`，增加AI模式选项：

```python
use_ai = serializers.BooleanField(
    default=False, 
    required=False,
    help_text="是否使用AI服务生成Markdown"
)
```

### 4. 完善错误处理和日志
- 为AI服务调用增加异常处理
- 添加详细日志记录
- 处理AI生成内容格式问题

## 实现步骤

1. **更新数据模型**
   - 在`ai_services/services/n8n_webhook/formats.py`中添加新的请求/响应模型
   - 在`TASK_FORMATS`字典中注册新任务类型

2. **扩展客户端方法**
   - 在`ai_services/services/n8n_webhook/client.py`添加生成Markdown的方法

3. **更新知识点到PPT服务**
   - 在`courses/services/knowledge_to_ppt.py`添加AI生成方法
   - 重构当前Markdown生成逻辑

4. **更新序列化器**
   - 在`courses/serializers_ppt.py`添加AI模式选项

5. **编写测试**
   - 为新功能添加单元测试和集成测试

## 测试计划

1. **单元测试**
   - 测试新数据模型的验证逻辑
   - 测试客户端扩展方法
   - 测试带AI模式和不带AI模式的Markdown生成

2. **集成测试**
   - 测试完整流程：知识点→AI生成Markdown→marp转换→PPT
   - 测试错误处理和异常情况

3. **AI生成内容验证**
   - 验证AI生成的Markdown是否保持知识点层次结构
   - 验证生成的Markdown是否符合marp-cli语法
   - 验证转换的PPT是否正确反映知识点层次

## 实现结果

### 1. 数据模型实现
✅ 在`ai_services/services/n8n_webhook/formats.py`中添加了:
- `KnowledgeToMarkdownRequestData`类，包含知识点数据、标题、课程信息等字段
- `KnowledgeToMarkdownResponseData`类，包含生成的Markdown和其他元数据
- 添加了响应格式化处理函数，支持从不同字段中提取Markdown内容

### 2. 客户端方法实现
✅ 在`ai_services/services/n8n_webhook/client.py`中添加了:
- `generate_markdown_from_knowledge`异步方法
- `generate_markdown_from_knowledge_sync`同步方法
- 使用适当的错误处理和异常捕获

### 3. 服务层集成
✅ 在`courses/services/knowledge_to_ppt.py`中:
- 添加了`generate_markdown_using_ai`方法，将知识点数据格式化为AI可处理的格式
- 优化了AI提示语构建，使AI更好地理解知识点层级结构
- 添加了自动修复功能，检测和添加缺失的marp前置元数据
- 实现了回退机制，在AI服务失败时使用本地生成逻辑

### 4. 序列化器更新
✅ 在`courses/serializers_ppt.py`中:
- 添加了`use_ai`字段，默认为False，让客户端可以选择是否使用AI生成

### 5. 测试结果
✅ 所有测试都成功通过:
- 单元测试验证了本地生成、AI生成和错误回退功能
- 集成测试验证了与真实AI服务的集成
- AI生成的Markdown保持了知识点层级结构
- 成功将AI生成的Markdown转换为PPTX文件

### 6. 性能与质量
- AI生成Markdown平均耗时约50-60秒
- 生成的PPTX文件大小约为200-300KB
- AI生成的内容质量明显优于本地生成，更加丰富和结构化

### 7. 状态
✅ 任务已完成并标记为done
