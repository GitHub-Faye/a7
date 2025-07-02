"""
n8n Webhook 请求/响应格式定义模块

使用Pydantic定义标准化的数据结构，用于验证和构建与n8n服务交互的数据。
"""

import json
import re
import logging
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, List, Optional

from .exceptions import N8nInvalidRequestError, N8nResponseError


logger = logging.getLogger(__name__)


# ==============================================================================
# 基础模型 (Base Models)
# ==============================================================================

class BaseRequest(BaseModel):
    """请求基础模型，所有请求模型应继承自此模型"""
    pass


class BaseResponse(BaseModel):
    """响应基础模型，所有响应模型应继承自此模型"""
    pass


# ==============================================================================
# RAG AI 任务格式 (RAG AI Task Formats)
# ==============================================================================

class RagAIRequestData(BaseRequest):
    """ragAI任务的请求数据模型"""
    chatInput: str = Field(..., description="用户输入的聊天内容")
    sessionId: str = Field(..., description="会话ID，用于跟踪多轮对话")


class RagAISource(BaseResponse):
    """ragAI任务响应中的来源信息模型"""
    title: str = Field(..., description="来源标题")
    url: str = Field(..., description="来源URL")


class RagAIResponseData(BaseResponse):
    """ragAI任务的响应数据模型"""
    answer: str = Field(..., description="AI生成的回答")
    sources: Optional[List[RagAISource]] = Field(default_factory=list, description="回答所依据的来源列表")


# ==============================================================================
# 课程内容生成任务格式 (Course Content Generation Task Formats)
# ==============================================================================

class CourseGenerationRequestData(BaseRequest):
    """课程内容生成任务的请求数据模型"""
    course_name: str = Field(..., description="课程名称")
    chapter_count: int = Field(..., gt=0, description="章节数量")
    course_description: str = Field(..., description="课程描述")
    subject: str = Field(..., description="学科")
    grade_level: str = Field(..., description="年级水平")
    additional_requirements: Optional[str] = Field(None, description="额外要求")
    chatInput: str = Field(..., description="生成课程的提示文本，包含课程知识点需求")
    sessionId: str = Field(..., description="会话ID，用于跟踪多轮对话")

class KnowledgePointData(BaseResponse):
    """知识点数据模型，支持层级结构"""
    title: str = Field(..., description="知识点标题")
    content: str = Field(..., description="知识点内容")
    importance: int = Field(..., ge=1, le=10, description="重要性(1-10)")
    children: List['KnowledgePointData'] = Field(default_factory=list, description="子知识点列表")

class CourseData(BaseResponse):
    """课程核心数据模型"""
    title: str = Field(..., description="课程标题")
    description: str = Field(..., description="课程描述")
    subject: str = Field(..., description="学科")
    grade_level: str = Field(..., description="年级水平")


class CourseGenerationResponseData(BaseResponse):
    """课程内容生成任务的响应数据模型"""
    course: CourseData = Field(..., description="生成的课程核心信息")
    knowledge_points: List[KnowledgePointData] = Field(..., description="生成的知识点层级结构")


# ==============================================================================
# 响应格式化和转换 (Response Formatting and Conversion)
# ==============================================================================

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    尝试从文本中提取JSON对象
    
    Args:
        text: 可能包含JSON的文本
        
    Returns:
        提取的JSON对象或None（如果无法提取）
    """
    # 首先尝试解析整个文本作为JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试使用正则表达式查找JSON格式的文本
    json_pattern = r'```(?:json)?\s*({[\s\S]*?})```'
    matches = re.findall(json_pattern, text)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # 最后尝试查找 { 和 } 之间的内容
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_str = text[start_idx:end_idx+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return None


def format_course_generation_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    尝试将n8n返回的数据格式化为符合CourseGenerationResponseData要求的结构
    
    Args:
        data: n8n返回的原始数据
        
    Returns:
        格式化后的数据，符合CourseGenerationResponseData结构
    
    Raises:
        N8nResponseError: 如果无法格式化数据
    """
    logger.info("正在格式化课程生成响应数据")
    
    # 情况1: 如果n8n返回的是带有answer字段的对象（常见于某些模型的返回格式）
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        answer_text = data['answer']
        logger.info(f"检测到带有answer字段的响应，尝试从中提取JSON。文本长度: {len(answer_text)}")
        
        # 尝试从answer中提取JSON
        extracted_json = extract_json_from_text(answer_text)
        if extracted_json:
            logger.info("成功从answer字段中提取JSON结构")
            return extracted_json
        else:
            logger.warning(f"无法从answer字段中提取有效JSON: {answer_text[:100]}...")
    
    # 情况2: 如果收到的是包含output字段的响应
    if isinstance(data, dict) and 'output' in data and isinstance(data['output'], str):
        text_output = data['output']
        logger.info(f"收到包含output字段的响应，尝试提取JSON。文本长度: {len(text_output)}")
        
        # 尝试从文本中提取JSON
        extracted_json = extract_json_from_text(text_output)
        if extracted_json:
            logger.info("成功从output字段中提取JSON结构")
            return extracted_json
        else:
            logger.warning(f"无法从output字段中提取有效JSON: {text_output[:100]}...")
    
    # 情况3: 检查数据是否已经符合期望的结构
    if isinstance(data, dict) and 'course' in data and 'knowledge_points' in data:
        logger.info("数据结构已符合期望格式")
        return data
    
    # 尝试创建一个基本的兼容结构
    try:
        # 如果数据本身是带有code blocks的字符串
        if isinstance(data, str):
            extracted_json = extract_json_from_text(data)
            if extracted_json:
                logger.info("成功从字符串响应中提取JSON结构")
                data = extracted_json
            else:
                logger.warning(f"无法从字符串响应中提取有效JSON: {data[:100]}...")
        
        # 如果缺少course字段，尝试构建
        if 'course' not in data and 'title' in data:
            logger.warning("正在从顶级字段构建course对象")
            course = {
                'title': data.get('title', 'Unknown Course'),
                'description': data.get('description', ''),
                'subject': data.get('subject', ''),
                'grade_level': data.get('grade_level', '')
            }
            data['course'] = course
        
        # 如果缺少knowledge_points字段，尝试从章节构建
        if 'knowledge_points' not in data and 'chapters' in data:
            logger.warning("正在从chapters构建knowledge_points")
            knowledge_points = []
            for i, chapter in enumerate(data['chapters']):
                if isinstance(chapter, dict):
                    kp = {
                        'title': chapter.get('title', f'Chapter {i+1}'),
                        'content': chapter.get('content', ''),
                        'importance': chapter.get('importance', 5),
                        'children': []
                    }
                    
                    # 尝试将topics或sections转换为children
                    if 'topics' in chapter and isinstance(chapter['topics'], list):
                        for j, topic in enumerate(chapter['topics']):
                            if isinstance(topic, dict):
                                child = {
                                    'title': topic.get('title', f'Topic {j+1}'),
                                    'content': topic.get('content', ''),
                                    'importance': topic.get('importance', 3),
                                    'children': []
                                }
                                kp['children'].append(child)
                    
                    knowledge_points.append(kp)
            
            data['knowledge_points'] = knowledge_points
        
        # 最后检查结构是否完整
        if isinstance(data, dict) and 'course' in data and 'knowledge_points' in data:
            return data
        
        # 如果仍然不符合结构，尝试构建最小可用结构
        logger.warning(f"尝试构建最小可用结构，原始数据: {str(data)[:200]}...")
        
        # 构建最小可用结构
        minimal_response = {
            "course": {
                "title": "Generated Course",
                "description": "系统生成的课程",
                "subject": "未指定",
                "grade_level": "未指定"
            },
            "knowledge_points": []
        }
        
        # 如果有一些数据可以使用，尝试填充
        if isinstance(data, dict):
            # 尝试更新课程信息
            if 'title' in data:
                minimal_response['course']['title'] = data['title']
            if 'description' in data:
                minimal_response['course']['description'] = data['description']
            if 'subject' in data:
                minimal_response['course']['subject'] = data['subject']
            if 'grade_level' in data:
                minimal_response['course']['grade_level'] = data['grade_level']
            
            # 如果有内容但格式不匹配，创建一个知识点
            minimal_response['knowledge_points'].append({
                "title": "自动生成的知识点",
                "content": f"无法解析原始数据，这是自动生成的内容。原始数据: {str(data)[:100]}...",
                "importance": 5,
                "children": []
            })
            
            return minimal_response
        
        # 如果仍然不符合结构，记录错误并抛出异常
        logger.error(f"无法格式化数据为有效的课程生成响应: {data}")
        raise N8nResponseError(
            message="无法解析AI服务返回的课程生成数据",
            error_data=data
        )
    
    except Exception as e:
        logger.exception(f"格式化课程生成响应时发生错误: {str(e)}")
        raise N8nResponseError(
            message=f"处理课程生成响应数据失败: {str(e)}",
            error_data=data
        )


# ==============================================================================
# 任务格式注册与管理 (Task Format Registry)
# ==============================================================================

# 定义一个任务格式注册表，用于存储不同任务类型的请求和响应模型
TASK_FORMATS: Dict[str, Dict[str, Any]] = {
    "ragAI": {
        "request": RagAIRequestData,
        "response": RagAIResponseData,
    },
    "courseGeneration": {
        "request": CourseGenerationRequestData,
        "response": CourseGenerationResponseData,
    },
    # 在这里可以添加其他任务类型的格式定义
    # "another_task": {
    #     "request": AnotherTaskRequest,
    #     "response": AnotherTaskResponse,
    # },
}


def get_task_format(task_type: str) -> Optional[Dict[str, Any]]:
    """
    根据任务类型获取对应的请求和响应模型
    
    Args:
        task_type: 任务类型字符串
        
    Returns:
        一个包含'request'和'response'模型的字典，如果未找到则返回None
    """
    return TASK_FORMATS.get(task_type)


def validate_request_data(task_type: str, data: Dict[str, Any]) -> BaseModel:
    """
    验证给定任务类型的请求数据
    
    Args:
        task_type: 任务类型字符串
        data: 要验证的请求数据
        
    Returns:
        一个已验证的Pydantic模型实例
        
    Raises:
        N8nInvalidRequestError: 如果任务类型无效或数据验证失败
    """
    task_format = get_task_format(task_type)
    if not task_format:
        raise N8nInvalidRequestError(f"不支持的任务类型: {task_type}")
        
    request_model = task_format.get("request")
    if not request_model:
        raise N8nInvalidRequestError(f"任务类型 '{task_type}' 未定义请求模型")
        
    try:
        validated_model = request_model(**data)
        return validated_model
    except ValidationError as e:
        # 将Pydantic的验证错误包装为自定义异常
        raise N8nInvalidRequestError(
            message=f"任务 '{task_type}' 的请求数据验证失败",
            validation_errors=e.errors()
        )


def parse_response(task_type: str, data: Dict[str, Any]) -> BaseModel:
    """
    解析和验证给定任务类型的响应数据

    Args:
        task_type: 任务类型字符串
        data: 从n8n收到的响应数据

    Returns:
        一个已验证的Pydantic响应模型实例

    Raises:
        N8nResponseError: 如果任务类型无效或数据验证失败
    """
    task_format = get_task_format(task_type)
    if not task_format:
        # 这种情况理论上不应发生，因为请求时已验证过
        raise N8nResponseError(f"不支持的任务类型: {task_type}")

    response_model = task_format.get("response")
    if not response_model:
        raise N8nResponseError(f"任务类型 '{task_type}' 未定义响应模型")

    # 对于课程生成任务，先尝试格式化响应
    if task_type == "courseGeneration":
        data = format_course_generation_response(data)

    try:
        validated_model = response_model.model_validate(data)
        return validated_model
    except ValidationError as e:
        # 将Pydantic的验证错误包装为我们的自定义响应异常
        raise N8nResponseError(
            message=f"任务 '{task_type}' 的响应数据格式无效",
            validation_errors=e.errors()
        ) 