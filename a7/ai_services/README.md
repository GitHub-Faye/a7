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