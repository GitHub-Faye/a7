# 任务16.4：Markdown到PPT转换实施计划

## 任务概述
任务16.4 "Convert Markdown to PPT"，目标是使用marp-cli Web API将经过验证的分层Markdown转换为PPT演示文稿，同时确保在输出中保留知识结构。

## 上下文分析

### 已完成的工作
1. **Marp服务模块**：已创建完整的marp_service应用，提供Markdown到各种演示格式(PDF/PPTX/HTML/PNG)的转换功能
2. **Markdown验证模块**：已实现MarkdownValidator类，可以验证和修复Markdown内容
3. **知识点到PPT服务**：已实现KnowledgePointToPPTService类，提供知识点获取、Markdown生成和转换流程
4. **API端点**：已设置好知识点到PPT转换的API端点和序列化器

### 现有关键功能
1. **marp_service.__init__.py**：提供顶层API `convert_markdown_to_format` 和 `convert_file_to_format`
2. **marp_service.cli**：提供MarpCLIBuilder和MarpCLIExecutor类，处理命令行参数和执行
3. **courses.services.knowledge_to_ppt**：提供KnowledgePointToPPTService类，包含：
   - `fetch_knowledge_points_hierarchy`：获取知识点层次结构
   - `generate_markdown_from_knowledge_points`：本地生成Markdown
   - `generate_markdown_using_ai`：使用AI生成Markdown
   - `validate_and_convert_markdown`：验证和转换Markdown
   - `process_knowledge_points_to_ppt`：完整处理流程

## 任务目标
实现 `validate_and_convert_markdown` 方法，完成Markdown到PPT演示文稿的转换功能，确保：
1. 适当处理验证逻辑，使用MarkdownValidator验证输入
2. 对验证失败的Markdown尝试自动修复
3. 调用marp_service的API进行实际转换
4. 正确管理临时文件和输出文件
5. 保留知识结构在生成的PPT中
6. 提供错误处理和日志记录

## 实现方案

### 具体步骤
1. **在KnowledgePointToPPTService类中实现validate_and_convert_markdown方法**：
   - 使用MarkdownValidator验证Markdown内容
   - 尝试修复无效的Markdown
   - 生成唯一文件名和输出路径
   - 调用marp_service.convert_markdown_to_format函数
   - 返回生成的文件路径和文件名

2. **测试实现**：
   - 单元测试：使用mock验证方法调用和参数传递
   - 集成测试：使用实际知识点数据生成Markdown并转换为PPT

### 代码实现细节
```python
def validate_and_convert_markdown(self, markdown: str, format: str = 'pptx', theme: str = 'default') -> Tuple[str, str]:
    """
    验证Markdown并调用marp服务转换为演示文稿
    
    Args:
        markdown: Markdown内容
        format: 输出格式(pptx, pdf, html)
        theme: 主题名称
        
    Returns:
        元组 (文件路径, 文件名)
    """
    # 创建验证器对象
    validator = MarkdownValidator(markdown)
    
    # 执行验证
    is_valid = validator.validate()
    
    # 如果存在问题，尝试修复
    if not is_valid:
        issues = validator.get_issues()
        logger.warning(f"Markdown验证发现问题: {issues}")
        
        # 尝试修复问题
        markdown = validator.fix()
        logger.info("已尝试修复Markdown问题")
        
        # 再次验证修复后的内容
        validator = MarkdownValidator(markdown)
        if not validator.validate():
            logger.warning(f"修复后仍然存在问题: {validator.get_issues()}")
    
    # 生成唯一文件名
    unique_id = str(uuid.uuid4())
    output_filename = f"presentation_{unique_id}.{format}"
    output_path = os.path.join(self.presentation_dir, output_filename)
    
    # 创建完整的物理路径
    full_output_path = os.path.join(settings.MEDIA_ROOT, output_path)
    
    try:
        # 调用marp服务进行转换
        convert_markdown_to_format(
            content=markdown,
            output_format=format,
            output_path=full_output_path,
            theme=theme
        )
        
        # 返回相对路径和文件名，用于构建URL
        return output_path, output_filename
    
    except Exception as e:
        logger.error(f"Markdown转换失败: {str(e)}")
        raise ValueError(f"Markdown转换失败: {str(e)}")
```

### 测试策略
1. **单元测试**：
   - 测试验证有效/无效Markdown的行为
   - 测试修复尝试
   - 测试转换成功/失败的情况
   - 测试不同格式和主题

2. **集成测试**：
   - 测试整个流程，从知识点数据到最终PPT文件
   - 验证生成的PPT是否正确保留了知识结构

## 风险与挑战
1. 处理Windows平台上的路径和命令执行（已有解决方案）
2. 确保临时文件正确清理，避免资源泄露
3. 验证生成的PPT是否保留层次结构

## 成功标准
1. `validate_and_convert_markdown`方法能够成功将验证过的Markdown转换为PPT
2. 自动修复功能能够处理常见的Markdown问题
3. 生成的PPT正确保留知识点的层次结构
4. 所有单元测试和集成测试通过
