# 问题格式化规则实现计划（任务13.4）

## 任务概述
实现针对AI生成问题的格式化规则和验证，确保生成的问题符合系统要求和教育标准。

## 当前状态分析
已完成的相关任务：
- 任务13.2：已实现API端点接收参数并调用AI模型
- 任务13.3：已定义AI请求格式和集成，创建了QuestionData和QuestionGenerationResponseData模型

目前的问题生成流程：
1. 客户端向`/api/questions-generate/`发送包含知识点ID、问题类型和数量的请求
2. QuestionGenerationViewSet处理请求，创建标准格式的chatInput
3. 通过N8nWebhookClient调用AI服务生成问题
4. AI返回的问题经过格式化后返回给客户端

## 实现计划

### 1. 定义问题类型的格式化规则
为每种题型（单选题、多选题、填空题、简答题、编程题等）定义明确的格式规范：

#### 单选题 (single_choice)
```python
{
  "title": "问题标题",
  "content": "清晰表述的问题内容",
  "type": "single_choice",
  "difficulty": 1-5,
  "answer_template": ["选项A", "选项B", "选项C", "选项D"],
  "knowledge_point_id": 知识点ID
}
```

#### 多选题 (multiple_choice)
```python
{
  "title": "问题标题",
  "content": "清晰表述的问题内容",
  "type": "multiple_choice",
  "difficulty": 1-5,
  "answer_template": ["选项A", "选项B", "选项C", "选项D"],
  "knowledge_point_id": 知识点ID
}
```

#### 填空题 (fill_blank)
```python
{
  "title": "问题标题",
  "content": "包含___或[BLANK]的问题内容",
  "type": "fill_blank",
  "difficulty": 1-5,
  "answer_template": ["答案1", "答案2"...],  # 可接受的答案列表
  "knowledge_point_id": 知识点ID
}
```

#### 简答题 (short_answer)
```python
{
  "title": "问题标题",
  "content": "需要学生回答的问题内容",
  "type": "short_answer",
  "difficulty": 1-5,
  "answer_template": "参考答案或评分要点",
  "knowledge_point_id": 知识点ID
}
```

#### 编程题 (coding)
```python
{
  "title": "问题标题",
  "content": "详细的编程题目要求",
  "type": "coding",
  "difficulty": 1-5,
  "answer_template": "示例代码或解题思路",
  "knowledge_point_id": 知识点ID
}
```

### 2. 创建问题格式验证服务

创建一个专门的验证服务类`QuestionFormatValidator`，负责验证问题格式：

```python
class QuestionFormatValidator:
    """问题格式验证器，负责验证AI生成的问题是否符合规范"""
    
    @staticmethod
    def validate_questions(questions):
        """验证问题列表格式"""
        validated_questions = []
        errors = []
        
        for i, question in enumerate(questions):
            try:
                validated = QuestionFormatValidator.validate_question(question)
                validated_questions.append(validated)
            except ValueError as e:
                errors.append(f"问题{i+1}格式错误: {str(e)}")
        
        return validated_questions, errors
    
    @staticmethod
    def validate_question(question):
        """验证单个问题格式"""
        # 基本字段验证
        required_fields = ['title', 'content', 'type', 'difficulty', 'knowledge_point_id']
        for field in required_fields:
            if field not in question:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 验证题型
        question_type = question['type']
        validator_method = getattr(
            QuestionFormatValidator, 
            f"validate_{question_type}_format", 
            None
        )
        
        if not validator_method:
            raise ValueError(f"不支持的题型: {question_type}")
        
        # 调用对应题型的验证方法
        return validator_method(question)
    
    @staticmethod
    def validate_single_choice_format(question):
        """验证单选题格式"""
        # 验证逻辑...
        return question
    
    @staticmethod
    def validate_multiple_choice_format(question):
        """验证多选题格式"""
        # 验证逻辑...
        return question
    
    # 其他题型的验证方法...
```

### 3. 增强问题生成提示（改进chatInput）

改进`QuestionGenerationViewSet`中的问题生成提示，针对不同题型添加明确的格式指导：

```python
# 根据请求的题型构建格式指南部分
format_guidelines = ""

if 'single_choice' in question_types:
    format_guidelines += """
单选题格式示例：
{
  "title": "短小的问题标题",
  "content": "完整的问题描述，包含必要背景",
  "type": "single_choice",
  "difficulty": 3,
  "answer_template": ["正确选项", "干扰选项1", "干扰选项2", "干扰选项3"],
  "knowledge_point_id": 知识点ID
}
"""

# 为其他题型添加类似格式指南

# 将格式指南添加到chatInput中
standard_chat_input = f"""
请根据以下知识点信息生成教学练习题，并以严格的JSON格式返回结果。

知识点信息：
{json.dumps(knowledge_points, ensure_ascii=False, indent=2)}

要求：
- 生成{quantity}道练习题
- 题目类型：{', '.join(question_types)}
- 难度等级：{difficulty if difficulty else '1-5之间'}

格式要求：
{format_guidelines}

你必须严格按照以下JSON格式返回结果，不要添加任何额外文本、说明或Markdown标记。
"""
```

### 4. 实现格式化方法集合

创建一个`QuestionFormatter`类，负责对题目进行格式化处理：

```python
class QuestionFormatter:
    """问题格式化工具，负责标准化AI生成的问题格式"""
    
    @staticmethod
    def format_questions(questions):
        """格式化问题列表"""
        formatted_questions = []
        
        for question in questions:
            formatter_method = getattr(
                QuestionFormatter,
                f"format_{question['type']}_question",
                QuestionFormatter.format_default_question
            )
            formatted = formatter_method(question)
            formatted_questions.append(formatted)
            
        return formatted_questions
    
    @staticmethod
    def format_single_choice_question(question):
        """格式化单选题"""
        # 确保answer_template是列表形式
        if isinstance(question.get('answer_template'), str):
            # 尝试解析字符串为列表
            try:
                import json
                question['answer_template'] = json.loads(question['answer_template'])
            except:
                # 如果无法解析，则转换为单元素列表
                question['answer_template'] = [question['answer_template']]
                
        return question
        
    # 为其他题型实现类似的格式化方法...
    
    @staticmethod
    def format_default_question(question):
        """默认格式化方法"""
        return question
```

### 5. 集成到现有视图和服务中

1. 修改`QuestionGenerationViewSet`中的`create`方法，加入格式验证：

```python
def create(self, request, *args, **kwargs):
    # ... 现有代码 ...
    
    try:
        # 调用AI服务生成问题
        client = N8nWebhookClient()
        ai_response = client.generate_questions_sync(task_data)
        
        # 获取生成的问题
        questions = ai_response.get('questions', [])
        
        # 验证并格式化问题
        validator = QuestionFormatValidator()
        formatted_questions, format_errors = validator.validate_questions(questions)
        
        # 如果存在格式错误
        if format_errors:
            return create_api_response(
                success=False,
                error_code="FORMAT_ERROR",
                message="问题格式错误",
                errors=format_errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 返回格式化后的问题
        return create_api_response(
            success=True,
            data={'questions': formatted_questions},
            message=f"成功生成{len(formatted_questions)}道问题",
            status_code=status.HTTP_201_CREATED
        )
        
    # ... 现有异常处理代码 ...
```

2. 增强`format_question_generation_response`方法，在格式化响应时应用问题格式规则：

```python
def format_question_generation_response(data: Dict[str, Any]) -> Dict[str, Any]:
    # ... 现有代码 ...
    
    # 如果成功提取或构建了问题列表
    if isinstance(data, dict) and 'questions' in data and isinstance(data['questions'], list):
        # 应用格式化规则
        formatter = QuestionFormatter()
        data['questions'] = formatter.format_questions(data['questions'])
        return data
        
    # ... 现有代码 ...
```

### 6. 添加测试用例

创建测试文件`test_question_format.py`，测试问题格式化和验证功能：

```python
from django.test import TestCase
from a7.ai_services.services.question_format import QuestionFormatValidator, QuestionFormatter

class QuestionFormatTests(TestCase):
    """测试问题格式化和验证功能"""
    
    def test_single_choice_validation(self):
        """测试单选题格式验证"""
        # 准备测试数据
        valid_question = {
            "title": "测试单选题",
            "content": "这是一道测试单选题",
            "type": "single_choice",
            "difficulty": 3,
            "answer_template": ["选项A", "选项B", "选项C", "选项D"],
            "knowledge_point_id": 1
        }
        
        # 测试有效数据
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([valid_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        
        # 测试无效数据（缺少必填字段）
        invalid_question = valid_question.copy()
        del invalid_question["answer_template"]
        result, errors = validator.validate_questions([invalid_question])
        self.assertEqual(len(result), 0)
        self.assertEqual(len(errors), 1)
    
    # 添加其他题型的测试...
    
    def test_formatter(self):
        """测试问题格式化功能"""
        # 测试字符串答案模板转列表
        question = {
            "title": "测试题",
            "content": "内容",
            "type": "single_choice",
            "difficulty": 3,
            "answer_template": "['A', 'B', 'C', 'D']",  # 字符串形式
            "knowledge_point_id": 1
        }
        
        formatter = QuestionFormatter()
        formatted = formatter.format_questions([question])[0]
        self.assertIsInstance(formatted["answer_template"], list)
```

## 实施步骤

1. 创建新文件`a7/ai_services/services/question_format.py`，实现格式验证和格式化功能
2. 修改`a7/ai_services/services/n8n_webhook/formats.py`，增强问题格式化逻辑
3. 更新`a7/courses/views.py`中的`QuestionGenerationViewSet`，集成格式验证
4. 创建测试文件`a7/ai_services/tests/test_question_format.py`
5. 运行测试，确保所有功能正常工作

## 预期输出

- 详细定义的题型格式规范
- 能够验证和格式化不同题型的服务类
- 改进的问题生成提示，引导AI生成符合规范的问题
- 完善的错误处理，能够捕获和报告格式问题
- 测试覆盖，确保功能正常工作
