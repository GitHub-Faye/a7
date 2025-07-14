# 任务19.1 执行计划 - 修改AI服务端点

## 任务概述
- **任务ID**: 19.1
- **任务标题**: 修改AI服务端点
- **父任务**: 任务19 - 重构AI服务为统一输入/输出标准
- **任务描述**: 更新所有AI服务端点，使其严格接受`chatInput`和`sessionId`作为输入，返回`answer`和`sources`作为输出
- **依赖任务**: 19.6 (收集现有AI服务信息) - 已完成

## 背景分析
通过检查父任务19和已完成的依赖任务19.6，我们得知项目中共有7个AI服务需要标准化:
1. 学生对话服务（dialogue_with_student）
2. 问题生成服务（generate_questions）
3. 练习题生成服务（generate_exercises）
4. 答案校正服务（correct_student_answer）
5. 课程内容生成服务（generate_course_content）
6. 知识点转Markdown服务（generate_markdown_from_knowledge）
7. 知识点转PPT服务（KnowledgePointToPPT）

## 当前实现分析
- 所有AI服务都通过`N8nWebhookClient`与n8n工作流平台集成
- 每个服务已有定制化的chatInput构建逻辑，用于控制AI输出内容
- 服务响应从n8n返回后，通过格式化函数从纯文本响应中解析结构化数据
- 现有格式化函数已包含从文本中提取各类信息的逻辑，可以复用

## 执行计划

### 第一阶段：集中管理chatInput构建逻辑
1. 创建新的`prompt_templates.py`文件，集中管理所有AI服务的提示模板：
   - 将所有服务的chatInput构建逻辑从各处集中到一个地方
   - 为每个服务创建专门的提示模板函数：
     ```python
     def build_student_dialogue_prompt(query, context=None):
         # 构建学生对话提示
         return f"学生问题: {query}\n上下文: {context if context else '无'}"
     
     def build_question_generation_prompt(knowledge_points, quantity, question_types, difficulty):
         # 构建问题生成提示
         # ...
     ```
   - 确保模板函数保持原有提示的有效性，同时支持新的输入输出标准

2. 修改`client.py`中的服务方法，使用新的提示模板：
   - 保持方法签名不变，但内部实现改为使用提示模板
   - 确保只向n8n传递`chatInput`和`sessionId`两个参数
   - 示例：
     ```python
     def dialogue_with_student(self, **kwargs):
         # 提取原始参数
         query = kwargs.get("query") or kwargs.get("chatInput")
         context = kwargs.get("context", {})
         session_id = kwargs.get("sessionId", str(uuid.uuid4()))
         
         # 使用提示模板构建chatInput
         chat_input = prompt_templates.build_student_dialogue_prompt(query, context)
         
         # 只传递chatInput和sessionId给n8n
         return self._send_to_n8n({
             "chatInput": chat_input,
             "sessionId": session_id
         })
     ```

### 第二阶段：统一响应解析逻辑
1. 修改`formats.py`中的所有格式化函数，处理统一的响应格式：
   - 每个函数接收包含`answer`和`sources`字段的响应
   - 从`answer`纯文本中解析所需的结构化数据
   - 从`sources`纯文本中提取知识来源引用（如果有）
   - 复用现有的文本解析逻辑，如正则表达式、JSON提取等

2. 创建基础解析工具函数：
   ```python
   def extract_structured_data_from_text(text):
       """从纯文本中提取结构化数据（如JSON、列表等）"""
       # 复用现有的提取逻辑
   
   def extract_sources_from_text(text):
       """从sources文本中提取知识来源引用"""
       # 提取引用、链接等
   ```

3. 更新每个服务的格式化函数，例如：
   ```python
   def format_student_dialogue_response(data):
       # 提取answer文本
       answer_text = data.get("answer", "")
       
       # 从answer文本中解析结构化数据
       structured_data = extract_structured_data_from_text(answer_text)
       
       # 提取sources文本（如果有）
       sources_text = data.get("sources", "")
       sources_data = extract_sources_from_text(sources_text) if sources_text else []
       
       # 构建响应数据
       response_data = {
           "answer": structured_data.get("answer", answer_text),
           "resources": structured_data.get("resources", []),
           "follow_up_questions": structured_data.get("follow_up_questions", []),
           "sources": sources_data
       }
       
       return DialogueResponseData(**response_data)
   ```

### 第三阶段：更新视图和序列化器
1. 更新所有视图集，确保它们：
   - 只向AI服务传递必要参数（通过提示模板处理）
   - 正确处理新的统一响应格式
   - 保持API响应结构不变，确保向后兼容

2. 示例更新：
   ```python
   # 在StudentDialogueViewSet中
   def create(self, request):
       serializer = self.get_serializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       
       # 获取会话ID
       session_id = get_or_create_session_id(request)
       
       # 准备数据（只传递必要参数）
       client = N8nWebhookClient()
       result = client.dialogue_with_student_sync(
           query=serializer.validated_data["query"],
           context=serializer.validated_data.get("context", {}),
           sessionId=session_id
       )
       
       # 添加会话ID到结果
       result["session_id"] = session_id
       
       # 返回标准API响应
       return create_api_response(
           success=True,
           data=result,
           message="对话请求处理成功",
           status_code=status.HTTP_200_OK
       )
   ```

### 第四阶段：单元测试
1. 更新测试以验证新的统一接口：
   - 测试chatInput构建逻辑
   - 测试从纯文本响应中解析结构化数据
   - 测试视图和序列化器的兼容性

2. 添加新的测试用例：
   ```python
   def test_prompt_template_student_dialogue():
       """测试学生对话提示模板"""
       query = "什么是人工智能？"
       context = {"previous_messages": [...]}
       prompt = prompt_templates.build_student_dialogue_prompt(query, context)
       
       # 验证提示包含必要信息
       assert query in prompt
       assert "previous_messages" in prompt
   
   def test_extract_structured_data():
       """测试从纯文本中提取结构化数据"""
       text = "回答：这是AI的解释\n\n资源：[资源1](链接1), [资源2](链接2)\n\n后续问题：问题1, 问题2"
       data = extract_structured_data_from_text(text)
       
       assert "answer" in data
       assert len(data["resources"]) == 2
       assert len(data["follow_up_questions"]) == 2
   ```

### 第五阶段：向后兼容处理与现有代码复用
1. 复用现有的文本解析逻辑：
   - 从`old_ai_servers.md`中识别并提取有用的解析函数
   - 将现有的正则表达式、JSON提取和结构化数据解析逻辑整合到新系统中
   - 保留特定服务的专有解析逻辑，但调整其工作于新的输入输出格式

2. 确保向后兼容：
   - 保持原有方法签名不变
   - 在内部重构实现，但对外接口保持一致
   - 为旧格式响应添加转换层，确保现有集成不受影响

3. 示例复用代码：
   ```python
   # 复用现有的问题提取逻辑
   def extract_questions_from_text(text):
       # 从old_ai_servers.md中复制的有效代码
       # 已被证明可以从AI文本响应中提取问题数据
       # ...
   
   # 在新的格式化函数中使用
   def format_question_generation_response(data):
       answer_text = data.get("answer", "")
       questions_data = extract_questions_from_text(answer_text)  # 复用现有逻辑
       
       # 处理提取的数据...
   ```

## 时间估计
- 第一阶段(集中管理chatInput构建逻辑): 5小时
- 第二阶段(统一响应解析逻辑): 4小时
- 第三阶段(更新视图和序列化器): 3小时
- 第四阶段(单元测试): 5小时
- 第五阶段(向后兼容处理与现有代码复用): 3小时
- 总计: 20小时工作量

## 潜在风险与缓解措施
1. **风险**: 提示模板变更可能影响AI输出质量
   **缓解**: 在修改前记录基准输出，确保新模板产生相同质量的结果
  
2. **风险**: 文本解析逻辑可能不适用于新的响应格式
   **缓解**: 创建健壮的解析函数，处理多种可能的输出格式，并添加适当的错误处理
  
3. **风险**: 向后兼容层可能增加复杂性
   **缓解**: 明确标记兼容代码，并计划在未来版本中逐步淘汰

4. **风险**: 测试覆盖不足可能导致未发现的问题
   **缓解**: 增加集成测试，验证端到端功能，特别关注边缘情况
