# A7项目现有AI服务信息

本文档收集了当前项目中所有使用AI的服务相关信息，包括它们如何定制ChatInput、如何提取AI的输出、以及如何使用提取到的内容。该文档作为后续AI服务标准化改造的参考依据。

## AI服务架构概述

A7项目的AI服务主要通过`N8nWebhookClient`与n8n工作流平台集成，提供多种AI功能。该客户端实现了异步和同步方法，支持向n8n平台发送请求并处理响应。

### 核心组件

1. **N8nWebhookClient**：位于`a7/ai_services/services/n8n_webhook/client.py`，负责与n8n平台通信
2. **数据模型**：位于`a7/ai_services/services/n8n_webhook/formats.py`，使用Pydantic定义请求/响应数据结构
3. **API端点**：位于`a7/ai_services/views.py`和`a7/courses/views.py`，提供RESTful API接口
4. **响应格式化**：位于`a7/ai_services/api_response.py`，提供统一的API响应格式

### 基础工作流程

1. 接收API请求（如问题生成、对话等）
2. 验证和准备请求数据
3. 构建chatInput和其他参数
4. 发送请求到n8n服务
5. 接收和解析AI响应
6. 提取和格式化所需内容
7. 返回标准化API响应

## 详细服务信息

### 1. 学生对话服务（dialogue_with_student）

**用途**：处理学生的问题和查询，提供AI生成的回答和相关资源。

#### ChatInput定制方式
```python
dialogue_data = {
    "chatInput": serializer.validated_data["query"],  # 直接使用学生的查询文本
    "sessionId": session_id,
    "context": serializer.validated_data.get("context", {})  # 可选上下文信息
}
```

#### 输出内容提取方法
通过`format_student_dialogue_response`函数从AI响应中提取结构化内容：
```python
def format_student_dialogue_response(data):
    # 提取AI回答文本
    answer_text = extract_text_from_response(data)
    
    # 尝试提取结构化数据
    structured_data = extract_structured_data(answer_text)
    
    # 构建标准响应格式
    response_data = {
        "answer": structured_data.get("answer", answer_text),
        "resources": structured_data.get("resources", []),
        "follow_up_questions": structured_data.get("follow_up_questions", [])
    }
    
    return DialogueResponseData(**response_data)
```

#### 提取内容的使用方式
通过`StudentDialogueViewSet`作为API端点返回给前端：
```python
# 在视图集的create方法中
result = client.dialogue_with_student_sync(dialogue_data)
result["session_id"] = session_id  # 添加会话ID用于多轮对话

# 使用标准化API响应格式返回
return create_api_response(
    success=True,
    data=result,
    message="对话请求处理成功",
    status_code=status.HTTP_200_OK
)
```

### 2. 问题生成服务（generate_questions）

**用途**：基于知识点生成各类练习题，支持多种题型和难度级别。

#### ChatInput定制方式
```python
# 如果客户端没有提供chatInput，则自动构建
if not chatInput:
    chatInput = f"请生成{quantity}道题型为{', '.join(question_types)}的{difficulty_text}问题，基于以下知识点："
    
    # 添加知识点信息
    for kp_id in knowledge_point_ids:
        kp = KnowledgePoint.objects.get(id=kp_id)
        chatInput += f"\n\n知识点 {kp_id}: {kp.title}\n{kp.content}"

question_data = {
    "knowledge_point_ids": knowledge_point_ids,
    "question_types": question_types,
    "quantity": quantity,
    "difficulty": difficulty,
    "chatInput": chatInput,
    "sessionId": session_id
}
```

#### 输出内容提取方法
通过`format_question_generation_response`函数处理：
```python
def format_question_generation_response(data):
    # 提取AI回答文本
    answer_text = extract_text_from_response(data)
    
    # 尝试从文本中提取问题数据
    questions_data = extract_questions_from_text(answer_text)
    
    # 处理每个问题，确保格式正确
    processed_questions = []
    for q in questions_data:
        # 处理答案模板格式（支持字符串或列表）
        if "answer_template" in q:
            if isinstance(q["answer_template"], str):
                # 尝试将字符串转换为列表（针对选择题）
                if q["type"] in ["single_choice", "multiple_choice"]:
                    q["answer_template"] = parse_options(q["answer_template"])
                    
        processed_questions.append(QuestionData(**q))
    
    # 构建响应数据
    return QuestionGenerationResponseData(questions=processed_questions)
```

#### 提取内容的使用方式
通过`QuestionGenerationViewSet`作为API端点返回给前端，并支持导出功能：
```python
# 普通响应
result = client.generate_questions_sync(request_data)

# 存储到会话中用于后续导出
request.session[f"generated_questions_{session_key}"] = result["questions"]

# 使用标准化API响应格式返回
return create_api_response(
    success=True,
    data={
        "questions": result["questions"],
        "session_key": session_key
    },
    message="问题生成成功",
    status_code=status.HTTP_200_OK
)

# 导出功能
@action(detail=False, methods=["get"])
def export(self, request):
    # 支持JSON和CSV格式导出
    exporter = QuestionExporter()
    if format == "json":
        file_data = exporter.export_as_json(questions)
        content_type = "application/json"
    elif format == "csv":
        file_data = exporter.export_as_csv(questions)
        content_type = "text/csv"
```

### 3. 练习题生成服务（generate_exercises）

**用途**：为学生生成练习题，但不保存到数据库，适合即时练习场景。

#### ChatInput定制方式
```python
exercise_data = {
    "query": query,
    "knowledge_content": knowledge_content if knowledge_content else None,
    "question_types": question_types if question_types else None,
    "quantity": quantity,
    "difficulty": difficulty,
    # n8n格式要求
    "chatInput": f"生成{quantity}道练习题，内容关于: {query}" + 
                 (f"\n基于以下知识点内容:\n{knowledge_content}" if knowledge_content else "") +
                 (f"\n题型要求: {', '.join(question_types)}" if question_types else "") +
                 (f"\n难度级别: {difficulty}/5" if difficulty else ""),
    "sessionId": session_id
}
```

#### 输出内容提取方法
通过`format_exercise_generation_response`函数处理：
```python
def format_exercise_generation_response(data):
    # 提取AI回答文本
    answer_text = extract_text_from_response(data)
    
    # 尝试从文本中提取练习题数据
    exercises = parse_exercise_text(answer_text)
    
    # 构建响应数据
    questions = []
    for exercise in exercises:
        question_data = {
            "title": exercise.get("title", ""),
            "content": exercise.get("content", ""),
            "type": exercise.get("type", ""),
            "difficulty": exercise.get("difficulty", 3),
            "answer_template": exercise.get("answer_template", None)
        }
        questions.append(QuestionData(**question_data))
    
    return ExerciseGenerationResponseData(questions=questions)
```

#### 提取内容的使用方式
通过`ExerciseGenerationViewSet`作为API端点返回给前端：
```python
# 调用n8n客户端
client = N8nWebhookClient()
result = client.generate_exercises_sync(exercise_data)

# 在响应中包含会话ID
result["session_id"] = session_id

# 使用标准化API响应格式返回
return create_api_response(
    success=True,
    data={
        "exercises": result["questions"],
        "session_id": session_id
    },
    message="练习题生成成功",
    status_code=status.HTTP_200_OK
)
```

### 4. 答案校正服务（correct_student_answer）

**用途**：评估学生提交的答案，返回正确性、得分和反馈信息。

#### ChatInput定制方式
```python
# 获取练习题详情
exercise = Exercise.objects.get(id=exercise_id)

# 根据题型构建不同的提示
if exercise.type == "single_choice" or exercise.type == "multiple_choice":
    prompt_template = (
        "请评估以下选择题的答案正确性：\n\n"
        f"题目：{exercise.content}\n\n"
        f"选项：{exercise.answer_template}\n\n"
        f"正确答案：{exercise.answer}\n\n"
        f"学生答案：{student_answer}\n\n"
        "请提供评估结果，包括是否正确、得分（0-100）、详细反馈和改进建议。"
    )
else:  # 简答题、填空题等
    prompt_template = (
        "请评估以下题目的答案：\n\n"
        f"题目类型：{exercise.get_type_display()}\n"
        f"题目：{exercise.content}\n\n"
        f"参考答案：{exercise.answer}\n\n"
        f"学生答案：{student_answer}\n\n"
        "请提供评估结果，包括是否正确、得分（0-100）、详细反馈、改进建议和解析说明。"
    )

correction_data = {
    "exercise_id": exercise_id,
    "exercise_content": exercise.content,
    "exercise_type": exercise.type,
    "reference_answer": exercise.answer,
    "student_answer": student_answer,
    # n8n格式要求
    "chatInput": prompt_template,
    "sessionId": session_id
}
```

#### 输出内容提取方法
通过`format_answer_correction_response`函数处理：
```python
def format_answer_correction_response(data):
    # 提取AI回答文本
    answer_text = extract_text_from_response(data)
    
    # 尝试提取结构化数据
    structured_data = extract_correction_data(answer_text)
    
    # 确保所有必要字段存在，并使用合适的默认值
    if "is_correct" not in structured_data:
        # 尝试从文本中判断正确性
        structured_data["is_correct"] = "正确" in answer_text.lower() or "correct" in answer_text.lower()
    
    if "score" not in structured_data:
        # 提取可能的分数
        score_matches = re.findall(r'得分[:：]?\s*(\d+(?:\.\d+)?)', answer_text)
        structured_data["score"] = float(score_matches[0]) if score_matches else (100 if structured_data["is_correct"] else 0)
    
    # 提取反馈、建议和解析
    if "feedback" not in structured_data:
        structured_data["feedback"] = answer_text
    
    # 构建标准响应格式
    return AnswerCorrectionResponseData(
        is_correct=structured_data.get("is_correct", False),
        score=structured_data.get("score", 0),
        feedback=structured_data.get("feedback", ""),
        improvement_suggestions=structured_data.get("improvement_suggestions", None),
        explanation=structured_data.get("explanation", None)
    )
```

#### 提取内容的使用方式
通过`StudentAnswerCorrectionViewSet`作为API端点返回给前端：
```python
# 调用n8n客户端
client = N8nWebhookClient()
result = client.correct_student_answer_sync(correction_data)

# 在响应中包含会话ID
result["session_id"] = session_id

# 使用标准化API响应格式返回
return create_api_response(
    success=True,
    data=result,
    message="答案评估成功",
    status_code=status.HTTP_200_OK
)
```

### 5. 课程内容生成服务（generate_course_content）

**用途**：生成课程内容结构，包括课程基本信息和知识点层级结构。

#### ChatInput定制方式
```python
# 准备chatInput
chatInput = (
    f"请为一门名为'{course_name}'的{grade_level}{subject}课程生成内容大纲，"
    f"要求包含{chapter_count}个主要知识点，每个知识点可以包含2-3个子知识点。\n\n"
    f"课程描述：{course_description}\n"
)

# 添加额外要求（如果有）
if additional_requirements:
    chatInput += f"\n额外要求：{additional_requirements}\n"

course_data = {
    "course_name": course_name,
    "chapter_count": chapter_count,
    "course_description": course_description,
    "subject": subject,
    "grade_level": grade_level,
    "additional_requirements": additional_requirements,
    "chatInput": chatInput,
    "sessionId": session_id
}
```

#### 输出内容提取方法
通过`format_course_generation_response`函数处理：
```python
def format_course_generation_response(data):
    # 提取AI回答文本
    answer_text = extract_text_from_response(data)
    
    # 尝试从文本中提取JSON数据
    structured_data = extract_json_from_text(answer_text)
    
    if not structured_data:
        # 如果无法提取JSON，尝试使用规则解析文本
        structured_data = parse_course_content_text(answer_text)
    
    # 验证和处理课程数据
    course_data = structured_data.get("course", {})
    
    # 验证和处理知识点数据
    knowledge_points = structured_data.get("knowledge_points", [])
    
    # 递归处理知识点层级结构
    processed_knowledge_points = []
    for kp in knowledge_points:
        processed_kp = process_knowledge_point(kp)
        processed_knowledge_points.append(processed_kp)
    
    # 构建响应数据
    return CourseGenerationResponseData(
        course=CourseData(**course_data),
        knowledge_points=processed_knowledge_points
    )
```

#### 提取内容的使用方式
在课程内容生成API中使用，可选择直接创建数据库记录：
```python
# 调用n8n客户端
client = N8nWebhookClient()
result = client.generate_course_content_sync(course_data)

# 是否直接创建记录
if create_records:
    # 使用KnowledgeConverter将AI生成的内容转换为数据库记录
    converter = KnowledgeConverter()
    course_instance, knowledge_points = converter.convert_to_models(
        result, request.user
    )
    
    # 返回创建的记录信息
    return create_api_response(
        success=True,
        data={
            "course": CourseSerializer(course_instance).data,
            "knowledge_points_count": len(knowledge_points)
        },
        message="课程内容已生成并保存",
        status_code=status.HTTP_201_CREATED
    )
else:
    # 仅返回生成的内容，不保存
    return create_api_response(
        success=True,
        data=result,
        message="课程内容已生成",
        status_code=status.HTTP_200_OK
    )
```

### 6. 知识点转Markdown服务（generate_markdown_from_knowledge）

**用途**：将知识点数据转换为演示文稿Markdown格式，用于后续生成PPT。

#### ChatInput定制方式
```python
# 准备chatInput
chatInput = (
    f"请将以下知识点数据转换为适合演示文稿的Markdown格式，"
    f"标题为：{title or '知识点演示'}"
)

# 添加主题要求（如果有）
if theme:
    chatInput += f"\n使用'{theme}'演示主题。"

markdown_data = {
    "knowledge_data": knowledge_data,
    "title": title,
    "include_course_info": include_course_info,
    "theme": theme,
    "chatInput": chatInput,
    "sessionId": session_id
}
```

#### 输出内容提取方法
通过`format_knowledge_to_markdown_response`函数处理：
```python
def format_knowledge_to_markdown_response(data):
    # 提取AI回答文本
    answer_text = extract_text_from_response(data)
    
    # 查找Markdown内容（通常位于```markdown 和 ``` 之间）
    markdown_pattern = r"```(?:markdown)?\s*([\s\S]+?)```"
    markdown_matches = re.findall(markdown_pattern, answer_text)
    
    markdown_content = ""
    if markdown_matches:
        # 使用找到的第一个Markdown块
        markdown_content = markdown_matches[0].strip()
    else:
        # 如果没有找到Markdown块，使用整个回答文本
        markdown_content = answer_text.strip()
    
    # 构建响应数据
    return KnowledgeToMarkdownResponseData(markdown=markdown_content)
```

#### 提取内容的使用方式
在知识点到PPT转换过程中使用，为后续的Marp或其他演示工具提供输入：
```python
# 调用n8n客户端
client = N8nWebhookClient()
result = client.generate_markdown_from_knowledge_sync(markdown_data)

# 提取Markdown内容
markdown_content = result["markdown"]

# 使用Marp将Markdown转换为演示文稿
marp_converter = MarpConverter(theme=theme)
presentation_file = marp_converter.convert(markdown_content, format=output_format)

# 返回结果
if direct_download:
    # 直接返回文件下载
    return FileResponse(
        open(presentation_file, "rb"),
        as_attachment=True,
        filename=filename
    )
else:
    # 返回文件路径或Base64内容
    return create_api_response(
        success=True,
        data={
            "file_path": presentation_file,
            "format": output_format
        },
        message=f"{output_format.upper()}文件已生成",
        status_code=status.HTTP_200_OK
    )
```

### 7. 知识点转PPT服务（KnowledgePointToPPT）

**用途**：将知识点数据转换为演示文稿（PPT、PDF或HTML），支持自定义主题和样式。

#### ChatInput定制方式
```python
# 将知识点数据转换为可读的JSON字符串
knowledge_json = json.dumps(knowledge_data, ensure_ascii=False, indent=2)

# 构建提示文本
prompt = "请将以下知识点数据转换为适用于marp-cli的Markdown格式，保持层级结构。"

if title:
    prompt += f" 演示标题为：{title}。"
    
if theme:
    prompt += f" 使用主题：{theme}。"
    
if include_course_info:
    prompt += " 包含课程信息。"
else:
    prompt += " 不需要包含课程信息。"
    
prompt += "\n\n知识点数据如下：\n```json\n" + knowledge_json + "\n```"

# 生成Markdown的要求
prompt += "\n\n生成的Markdown应满足以下要求："
prompt += "\n1. 符合marp-cli的语法，以---分隔幻灯片"
prompt += "\n2. 以marp前置元数据开头，包含marp: true, theme: default, paginate: true等配置"
prompt += "\n3. 保持知识点的层级结构，标题级别反映层级关系"
prompt += "\n4. 第一张幻灯片为标题页，包含演示标题"
prompt += "\n5. 每个知识点应有独立的幻灯片"
prompt += "\n6. 给每张幻灯片添加适当的格式，如标题、正文、列表等"

# 准备请求数据
request_data = {
    "knowledge_data": knowledge_data,
    "title": title,
    "include_course_info": include_course_info,
    "theme": theme,
    "chatInput": prompt,
    "sessionId": session_id
}
```

#### 输出内容提取方法
通过直接从响应中获取markdown字段：
```python
# 调用AI服务
response = client.generate_markdown_from_knowledge_sync(request_data)

# 提取Markdown内容
if response and "markdown" in response:
    markdown_content = response["markdown"]
    
    # 确保Markdown以marp前置元数据开头
    if not markdown_content.strip().startswith("---"):
        marp_header = "---\nmarp: true\ntheme: default\npaginate: true\n---\n\n"
        markdown_content = marp_header + markdown_content
    
    return markdown_content
```

#### 提取内容的使用方式
将AI生成的Markdown内容通过Marp服务转换为演示文稿：
```python
# 1. 获取知识点层次结构
knowledge_data = self.fetch_knowledge_points_hierarchy(
    data["knowledge_point_ids"],
    data.get("include_children", True),
    data.get("max_depth", 3)
)

# 2. 使用AI服务生成Markdown
if use_ai:
    markdown_content = self.generate_markdown_using_ai(
        knowledge_data,
        data.get("title"),
        data.get("include_course_info", True),
        theme
    )
else:
    # 使用本地逻辑生成Markdown
    markdown_content = self.generate_markdown_from_knowledge_points(...)

# 3. 验证并转换Markdown为演示文稿
output_path, filename = self.validate_and_convert_markdown(
    markdown_content,
    data.get("format", "pptx"),
    theme,
    style_options=style_options
)

# 4. 返回文件URL
return {
    "status": "success",
    "data": {
        "file_url": f"{media_url}{output_path}",
        "filename": filename
    }
}
```

这个服务在KnowledgePointToPPTViewSet视图集中使用，为课程知识点创建精美的演示文稿。它与前面的"知识点转Markdown服务"相互补充，但功能更全面，包含了从知识点获取到最终演示文稿生成的完整流程，并支持多种输出格式（PPTX、PDF、HTML）和主题样式。

## 共同特点

通过分析上述各个AI服务，可以发现它们具有以下共同特点：

1. **输入格式**：
   - 所有服务都使用`chatInput`作为与AI交互的主要输入
   - 使用`sessionId`跟踪多轮对话或相关请求
   - 根据不同的场景定制额外的参数

2. **输出格式**：
   - AI服务的输出主要包含在`answer`字段中
   - 使用正则表达式或解析函数从原始响应中提取结构化数据
   - 将提取的数据映射到预定义的响应模型（Pydantic模型）

3. **API响应格式**：
   - 所有API端点使用统一的响应格式（通过`create_api_response`函数）
   - 响应包含`success`状态、`data`内容、`message`消息和状态码
   - 错误处理统一，包含错误代码和详细信息

4. **异步支持**：
   - 所有服务提供异步和同步两种调用方式（如`dialogue_with_student`和`dialogue_with_student_sync`）
   - 异步方法适用于高并发场景，同步方法适用于简单调用

## 结论

A7项目中的AI服务已形成了一套相对成熟的模式，但每个服务仍有各自独特的输入输出定制方式。统一这些服务的输入/输出标准将有助于提高代码可维护性和系统一致性。特别是需要将所有服务统一为仅接受`chatInput`和`sessionId`作为输入，并返回`answer`和`sources`作为输出，同时保留现有的定制提示和内容提取逻辑。
