# 使用真实n8n环境测试计划

## 任务概述

任务6.6要求使用真实的n8n环境对已开发的n8n Webhook服务进行测试。该服务的主要功能是与n8n工作流平台进行交互，用于处理AI服务请求，特别是"ragAI"类型的任务处理。

## 当前系统实现状况

从代码分析中我们了解到:

1. **已实现的组件**:
   - `WebhookConfig` 和 `WebhookCallLog` 模型用于配置管理和日志记录
   - `N8nWebhookClient` 客户端类，实现与n8n的异步和同步通信
   - `N8nWebhookAPIView` API视图，处理前端请求并转发到n8n服务
   - 请求/响应格式验证与标准化处理
   - 异常处理机制

2. **现有测试**:
   - 单元测试已覆盖API视图和客户端类的主要功能
   - 模拟测试了各种错误情况处理
   - 包含一个标记为`@pytest.mark.integration`的真实测试函数(`test_real_n8n_workflow`)

## 测试计划

### 1. 准备工作

1. **设置n8n测试环境**:
   - 使用已配置好的n8n实例
   - 使用RAG AI类型的工作流节点
   - 使用提供的Webhook URL: http://localhost:5678/webhook-test/bf4dd093-bb02-472c-9454-7ab9af97bd1d

2. **环境配置**:
   - 配置文件中的`N8N_WEBHOOK_URL`
   - 为测试创建对应的`WebhookConfig`记录，指向测试工作流

### 2. 基础功能测试

1. **API连通性测试**:
   - 向`/api/ai-services/webhook/`发送基本请求
   - 验证能够成功与n8n通信并获取响应
   - 检查`WebhookCallLog`记录是否正确创建

2. **请求参数验证测试**:
   - 测试RAG AI任务类型的请求参数验证
   - 测试缺少必要字段的情况
   - 验证错误信息是否准确

3. **响应处理测试**:
   - 验证API返回的响应格式是否符合预期
   - 测试响应中的源引用信息是否正确
   - 检查异常情况下的错误信息格式


## 测试实现方法



### 2. 测试函数实现

1. **使用现有`test_real_n8n_workflow`函数**:
   - 修改webhook_url为正确的节点地址
   
   ```python
   @pytest.mark.asyncio
   @pytest.mark.integration
   async def test_real_n8n_workflow(self):
       """
       使用真实的n8n工作流进行集成测试
       """
       # 创建实际的webhook配置
       create_webhook = sync_to_async(WebhookConfig.objects.create)
       webhook_config = await create_webhook(
           name="RAG AI测试Webhook",
           url="http://localhost:5678/webhook-test/bf4dd093-bb02-472c-9454-7ab9af97bd1d",
           headers={"Content-Type": "application/json"}
       )
       
       # 创建客户端
       client = N8nWebhookClient(webhook_config=webhook_config)
       
       # 准备测试数据
       test_data = {
           "chatInput": "今天天气怎么样?",
           "sessionId": "test_session_456"
       }
       
       try:
           # 发送实际请求到n8n工作流
           print("\n正在向n8n RAG AI工作流发送请求...")
           result = await client.send_request(test_data)
           
           # 验证结果
           assert isinstance(result, dict)
           assert "answer" in result
           assert isinstance(result["answer"], str)
           assert "sources" in result
           
           print(f"\n✅ 成功收到n8n工作流响应:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
           
           # 验证日志记录
           get_first_log = sync_to_async(lambda: WebhookCallLog.objects.filter(webhook=webhook_config).first())
           log = await get_first_log()
           assert log is not None
           assert log.status == "success"
           assert log.request_data == test_data
           print(f"\n✅ 成功记录webhook调用日志，执行时间: {log.execution_time:.2f}秒")
           
       except Exception as e:
           pytest.fail(f"\n❌ 测试失败: {str(e)}")
   ```





## 预期结果

1. 确认n8n Webhook服务能在真实环境下正常处理RAG AI请求
2. 验证请求/响应格式符合预期
3. 确认WebhookCallLog记录正确保存

## 后续步骤

1. 根据测试结果确认功能是否正常
2. 完成任务6.6的相关文档
