# 任务7.2实施计划：n8n Webhook集成服务

## 任务概述
实现n8n Webhook集成服务，建立与n8n AI服务的通信，用于发送生成请求和接收响应。此服务将处理与n8n端点的HTTP通信，包括请求格式化和响应解析。

## 依赖分析
- 任务依赖于任务1（已完成）：项目初始化和基础架构已设置
- 任务7的上级任务依赖于任务5（已完成）：课程内容管理API已实现
- 任务7的上级任务依赖于任务6（已完成）：AI服务集成基础架构已建立
  - 审查已完成的任务6显示：基础的n8n webhook服务已实现，包括客户端、异常处理和响应格式化
  - 已有通用AI任务处理框架，支持ragAI任务类型
  - 已有一个基本的课程生成数据模型但需要扩展实现

## 相关代码结构分析
基于现有项目结构，我们将处理以下文件：

1. **`a7/ai_services/services/n8n_webhook/formats.py`**
   - 已包含基础请求/响应模型结构
   - 已有CourseGenerationRequestData和CourseGenerationResponseData基础模型
   - 已注册了"courseGeneration"任务类型
   - 需要完善课程内容生成相关的数据模型

2. **`a7/ai_services/services/n8n_webhook/client.py`**
   - 已有N8nWebhookClient类，提供异步请求发送机制
   - 已有通用AI任务处理方法process_ai_task和process_ai_task_sync
   - 需添加课程内容生成的专用方法

3. **`a7/ai_services/services/n8n_webhook/exceptions.py`**
   - 已有完整的异常层次结构
   - 包含基础异常N8nWebhookError
   - 包含连接(N8nConnectionError)、超时(N8nTimeoutError)、响应(N8nResponseError)和请求验证(N8nInvalidRequestError)异常

4. **`a7/ai_services/views.py`**
   - 已有N8nWebhookAPIView视图处理POST请求
   - 提供通用任务处理机制
   - 需要确保能处理课程生成类型的任务

5. **`a7/ai_services/models.py`**
   - 已有WebhookConfig和WebhookCallLog模型
   - 提供webhook配置存储和调用日志功能

## 详细设计

### 1. 完善请求/响应模型
在`formats.py`文件中，我们需要：

- 完善现有的CourseGenerationRequestData模型：
  ```python
  class CourseGenerationRequestData(BaseRequest):
      """课程内容生成任务的请求数据模型"""
      course_name: str = Field(..., description="课程名称")
      chapter_count: int = Field(..., gt=0, description="章节数量")
      course_description: str = Field(..., description="课程描述")
      subject: str = Field(..., description="学科")
      grade_level: str = Field(..., description="年级水平")
      additional_requirements: Optional[str] = Field(None, description="额外要求")
  ```

- 完善KnowledgePointData和CourseGenerationResponseData模型：
  ```python
  class KnowledgePointData(BaseResponse):
      """知识点数据模型，支持层级结构"""
      title: str = Field(..., description="知识点标题")
      content: str = Field(..., description="知识点内容")
      importance: int = Field(..., ge=1, le=10, description="重要性(1-10)")
      children: List['KnowledgePointData'] = Field(default_factory=list, description="子知识点列表")

  class CourseGenerationResponseData(BaseResponse):
      """课程内容生成任务的响应数据模型"""
      course: CourseData = Field(..., description="生成的课程核心信息")
      knowledge_points: List[KnowledgePointData] = Field(..., description="生成的知识点层级结构")
  ```

### 2. 扩展客户端方法
在`client.py`文件中，扩展N8nWebhookClient类：

```python
async def generate_course_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成课程内容的异步方法
    
    Args:
        request_data: 课程生成请求数据，包含课程名称、章节数等
            
    Returns:
        Dict[str, Any]: 生成的课程内容，包含课程信息和知识点层级结构
    """
    return await self.process_ai_task("courseGeneration", request_data)

def generate_course_content_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成课程内容的同步方法
    
    Args:
        request_data: 课程生成请求数据，包含课程名称、章节数等
            
    Returns:
        Dict[str, Any]: 生成的课程内容，包含课程信息和知识点层级结构
    """
    return asyncio.run(self.generate_course_content(request_data))
```

### 3. 数据转换模块设计
创建一个新的转换模块用于将AI生成的内容转换为应用内部的知识点模型：

```python
from typing import Dict, List, Any
from courses.models import Course, KnowledgePoint
from django.db import transaction

def convert_ai_response_to_knowledge_points(course: Course, response_data: Dict[str, Any]) -> List[KnowledgePoint]:
    """
    将AI生成的课程内容转换为知识点模型对象
    
    Args:
        course: 课程对象，知识点将关联到此课程
        response_data: AI生成的响应数据，包含知识点结构
        
    Returns:
        List[KnowledgePoint]: 创建的顶级知识点列表
    """
    knowledge_points = []
    
    # 处理生成的知识点列表
    for kp_data in response_data.get('knowledge_points', []):
        # 创建顶级知识点
        knowledge_point = _create_knowledge_point(course, kp_data)
        knowledge_points.append(knowledge_point)
        
    return knowledge_points

def _create_knowledge_point(course: Course, kp_data: Dict[str, Any], parent=None) -> KnowledgePoint:
    """
    递归创建知识点及其子知识点
    
    Args:
        course: 知识点所属课程
        kp_data: 知识点数据
        parent: 父知识点（如果有）
        
    Returns:
        KnowledgePoint: 创建的知识点对象
    """
    # 创建知识点
    knowledge_point = KnowledgePoint(
        course=course,
        parent=parent,
        title=kp_data['title'],
        content=kp_data['content'],
        importance=kp_data.get('importance', 5)  # 默认重要性为5
    )
    knowledge_point.save()
    
    # 递归创建子知识点
    for child_data in kp_data.get('children', []):
        _create_knowledge_point(course, child_data, knowledge_point)
        
    return knowledge_point

@transaction.atomic
def create_course_with_knowledge_points(data: Dict[str, Any], user=None) -> Course:
    """
    创建课程并附带知识点结构
    
    Args:
        data: 包含课程信息和知识点结构的数据
        user: 创建课程的用户（教师）
        
    Returns:
        Course: 创建的课程对象
    """
    # 创建课程
    course_data = data.get('course', {})
    course = Course(
        title=course_data.get('title'),
        description=course_data.get('description'),
        subject=course_data.get('subject'),
        grade_level=course_data.get('grade_level'),
        teacher=user
    )
    course.save()
    
    # 创建知识点结构
    convert_ai_response_to_knowledge_points(course, data)
    
    return course
```

### 4. 集成到API视图
确保`views.py`中的N8nWebhookAPIView能处理课程生成任务：

现有视图可以通过通用的process_ai_task_sync方法处理任何已注册的任务类型，包括"courseGeneration"。不需要修改，但应该添加关于支持"courseGeneration"任务类型的文档注释。

## 实施步骤

### 第一阶段：模型定义和客户端扩展

1. **完善数据模型**
   - 检查并完善`formats.py`中的CourseGenerationRequestData和CourseGenerationResponseData模型
   - 确保所有必要字段都已定义，特别是知识点的层级结构

2. **扩展客户端方法**
   - 在N8nWebhookClient类中添加generate_course_content和generate_course_content_sync方法
   - 确保方法适当调用现有的process_ai_task和process_ai_task_sync函数
   - 添加详细的文档注释

### 第二阶段：数据转换模块

1. **创建转换模块**
   - 创建新文件`a7/ai_services/services/knowledge_converter.py`
   - 实现convert_ai_response_to_knowledge_points函数
   - 实现_create_knowledge_point辅助函数
   - 实现create_course_with_knowledge_points函数

2. **集成与服务层连接**
   - 将转换模块与客户端方法集成
   - 确保数据转换过程中的错误处理

### 第三阶段：测试和文档

1. **单元测试**
   - 为数据模型编写测试
   - 为客户端扩展方法编写测试
   - 为数据转换模块编写测试

2. **集成测试**
   - 编写完整的端到端测试，从API调用到知识点创建

3. **编写文档**
   - 更新API文档，添加课程生成任务的说明
   - 为数据模型和客户端方法添加详细注释

## 测试策略

### 1. 单元测试

#### 数据模型测试
- 测试CourseGenerationRequestData的验证
  - 确保必填字段验证正常工作
  - 测试章节数量的限制(>0)
  - 测试可选字段的处理
- 测试CourseGenerationResponseData的验证
  - 测试课程数据和知识点结构的验证
  - 测试层级知识点结构的验证

#### 客户端方法测试
- 测试generate_course_content方法
  - 模拟成功的API调用
  - 模拟超时和连接错误
  - 模拟响应验证错误

#### 数据转换模块测试
- 测试convert_ai_response_to_knowledge_points函数
  - 使用样例响应数据
  - 验证生成的知识点结构是否正确
- 测试边缘情况，如空知识点列表

### 2. 集成测试
- 创建模拟n8n服务器响应
- 测试完整的API调用流程
- 验证数据库中创建的知识点结构

## 注意事项

1. **异步处理**：确保异步方法在Django环境中正确工作，特别是涉及数据库操作时使用sync_to_async包装器。

2. **数据验证**：确保所有输入和输出数据严格验证，防止无效数据导致服务失败。

3. **错误处理**：提供详细的错误信息，特别是关于AI生成内容格式不正确的情况。

4. **大型响应处理**：考虑AI可能生成大量知识点的情况，确保系统能有效处理。

5. **事务完整性**：使用数据库事务确保知识点创建的完整性，防止部分创建导致数据不一致。

## 输出成果

1. 完善的课程生成请求/响应数据模型
2. 扩展的N8nWebhookClient，支持课程内容生成
3. 用于将AI响应转换为知识点模型的转换模块
4. 全面的测试套件，验证功能正确性
5. 详细的API文档，包括请求示例和响应示例
