# AI 服务应用

本应用提供了与n8n工作流程平台集成的AI服务功能，主要通过Webhook与n8n进行交互。

## 功能特点

- 提供标准化的AI服务抽象接口
- 支持异步和同步Webhook调用
- 完整的错误处理和异常分类
- 自动记录调用日志和性能指标
- 可配置的Webhook端点和头部信息

## 配置说明

在项目的`.env`文件中添加以下配置：

```
# n8n Webhook配置
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/path
N8N_WEBHOOK_AUTH_TOKEN=your-webhook-auth-token

# Aiohttp客户端配置
AIOHTTP_CLIENT_TIMEOUT=30  # 请求超时时间（秒）
```

## API使用示例

### 发送AI任务请求

```python
import requests

# API端点
url = "http://yourapp.com/api/ai/webhook/"

# 请求头
headers = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/json"
}

# 请求数据
data = {
    "task_type": "text_generation",  # 任务类型
    "data": {
        "prompt": "给我讲一个关于AI的故事",
        "max_tokens": 500
    }
}

# 发送请求
response = requests.post(url, json=data, headers=headers)

# 处理响应
if response.status_code == 200:
    result = response.json()
    print(f"生成的文本: {result.get('generated_text')}")
else:
    print(f"错误: {response.status_code}, {response.text}")
```

## Webhook配置管理

通过Django管理界面(`/admin/ai_services/webhookconfig/`)可以管理多个Webhook配置。每个配置可以包含：

- 名称和描述
- Webhook URL
- 请求头信息（如认证令牌）
- 活动状态（启用/禁用）

## 错误处理

服务层会捕获并分类以下类型的错误：

- `N8nConnectionError`: 连接错误
- `N8nTimeoutError`: 请求超时
- `N8nResponseError`: 响应错误（如状态码4xx或5xx）

所有错误都会被记录到日志中，并在API响应中返回适当的状态码和错误信息。 

## 学生助手对话API

学生助手对话API提供了一个端点，允许学生与AI助手进行对话交互。这个API支持多轮对话，可以记住对话上下文。

### API端点

- **URL**: `/api/student-dialogue/`
- **方法**: POST
- **权限**: 允许匿名访问（无需认证）

### 请求格式

```json
{
  "query": "什么是机器学习？",
  "session_id": "可选，如果不提供将自动生成",
  "context": {
    "可选上下文信息": "例如课程ID等"
  }
}
```

### 响应格式

```json
{
  "success": true,
  "status_code": 200,
  "message": "对话请求处理成功",
  "data": {
    "answer": "机器学习是人工智能的一个子领域，它使用统计技术让计算机能够从数据中"学习"（即逐步提高性能）而无需明确编程。",
    "resources": [
      {
        "title": "机器学习基础",
        "content": "机器学习介绍与基本概念",
        "type": "知识点",
        "id": 1
      }
    ],
    "follow_up_questions": ["什么是深度学习？", "机器学习有哪些应用？"],
    "session_id": "对话会话ID，用于多轮对话"
  }
}
```

### 错误响应

```json
{
  "success": false,
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "请求参数验证失败",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "query": ["此字段不能为空。"]
    }
  }
}
```

### 多轮对话

要进行多轮对话，请在后续请求中包含相同的`session_id`。这样AI助手就能记住之前的对话内容。

## 测试

### 运行测试

我们提供了一个测试脚本，可以方便地运行所有测试：

```bash
# 运行所有测试（单元测试和集成测试）
python run_student_dialogue_tests.py

# 只运行单元测试
python run_student_dialogue_tests.py --unit-only

# 只运行集成测试（需要n8n服务可用）
python run_student_dialogue_tests.py --integration-only
```

### 测试类型

1. **单元测试** (`test_student_dialogue.py`): 测试API的基本功能，使用模拟对象代替实际的n8n服务。

2. **错误处理测试** (`test_student_dialogue_integration.py`中的`StudentDialogueErrorHandlingTest`): 测试API的错误处理能力，包括验证错误、n8n服务错误等。

3. **集成测试** (`test_student_dialogue_integration.py`中的`StudentDialogueIntegrationTest`): 测试API与真实n8n服务的集成，包括单轮对话和多轮对话。这些测试需要n8n服务可用。

### 注意事项

- 集成测试需要n8n服务可用，并且配置了正确的webhook URL。如果n8n服务不可用，集成测试将失败。
- 集成测试会实际调用n8n服务，可能会产生API调用费用。
- 集成测试的响应会打印到控制台，便于手动检查。 