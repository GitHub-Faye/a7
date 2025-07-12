"""
n8n Webhook 请求/响应格式定义模块

使用Pydantic定义标准化的数据结构，用于验证和构建与n8n服务交互的数据。
"""

import json
import re
import uuid
import logging
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, List, Optional, Union

from .exceptions import N8nInvalidRequestError, N8nResponseError
from .logger import logger

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
# 学生对话任务格式 (Student Dialogue Task Formats)
# ==============================================================================

class DialogueRequestData(BaseRequest):
    """学生对话任务的请求数据模型"""
    chatInput: str = Field(..., description="学生的问题或查询文本")
    sessionId: str = Field(..., description="会话ID，用于跟踪多轮对话")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="可选上下文信息，如当前学习内容")


class DialogueResource(BaseResponse):
    """学生对话响应中的参考资源信息模型"""
    title: str = Field(..., description="资源标题")
    content: str = Field(..., description="资源内容摘要")
    type: str = Field(..., description="资源类型，如'知识点'、'课程'等")
    id: Optional[int] = Field(None, description="资源在系统中的ID")


class DialogueResponseData(BaseResponse):
    """学生对话任务的响应数据模型"""
    answer: str = Field(..., description="AI助手的回答")
    resources: Optional[List[DialogueResource]] = Field(default_factory=list, description="相关参考资源列表")
    follow_up_questions: Optional[List[str]] = Field(default_factory=list, description="可能的后续问题建议")


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
# 问题生成任务格式 (Question Generation Task Formats)
# ==============================================================================

class QuestionGenerationRequestData(BaseRequest):
    """问题生成任务的请求数据模型"""
    knowledge_point_ids: List[int] = Field(..., description="知识点ID列表")
    question_types: List[str] = Field(..., description="问题类型列表")
    quantity: int = Field(..., gt=0, le=50, description="生成问题的数量")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="问题难度(1-5)")
    chatInput: str = Field(..., description="生成问题的提示文本")
    sessionId: str = Field(..., description="会话ID，用于跟踪多轮对话")


class QuestionData(BaseResponse):
    """问题数据模型"""
    title: str = Field(..., description="问题标题")
    content: str = Field(..., description="问题内容")
    type: str = Field(..., description="问题类型")
    difficulty: int = Field(..., ge=1, le=5, description="难度等级(1-5)")
    answer_template: Optional[Union[str, List[str]]] = Field(None, description="答案模板或选项列表")
    knowledge_point_id: Optional[int] = Field(None, description="关联知识点ID")


class QuestionGenerationResponseData(BaseResponse):
    """问题生成任务的响应数据模型"""
    questions: List[QuestionData] = Field(..., description="生成的问题列表")


# ==============================================================================
# 知识点到Markdown转换任务格式 (Knowledge to Markdown Task Formats)
# ==============================================================================

class KnowledgeToMarkdownRequestData(BaseRequest):
    """知识点到Markdown转换任务的请求数据模型"""
    knowledge_data: Dict[str, Any] = Field(..., description="知识点数据结构，包含知识点及其层级关系")
    title: Optional[str] = Field(None, description="演示文稿标题")
    include_course_info: bool = Field(True, description="是否包含课程信息")
    theme: Optional[str] = Field(None, description="演示文稿主题")
    chatInput: str = Field(..., description="生成Markdown的提示文本")
    sessionId: str = Field(..., description="会话ID，用于跟踪多轮对话")


class KnowledgeToMarkdownResponseData(BaseResponse):
    """知识点到Markdown转换任务的响应数据模型"""
    markdown: str = Field(..., description="生成的Markdown内容")


# ==============================================================================
# 练习题生成任务格式 (Exercise Generation Task Formats)
# ==============================================================================

class ExerciseGenerationRequestData(BaseRequest):
    """练习题生成任务的请求数据模型"""
    chatInput: str = Field(..., description="生成练习题的提示文本")
    sessionId: str = Field(..., description="会话ID，用于跟踪多轮对话")


class ExerciseGenerationResponseData(BaseResponse):
    """练习题生成任务的响应数据模型"""
    questions: List[QuestionData] = Field(..., description="生成的练习题列表")
    session_id: str = Field(..., description="会话ID，用于后续答案提交和评估")


# ==============================================================================
# 答案校正任务格式 (Answer Correction Task Formats)
# ==============================================================================

class AnswerCorrectionResponseData(BaseResponse):
    """答案校正任务的响应数据模型"""
    is_correct: bool = Field(..., description="答案是否正确")
    score: float = Field(..., ge=0, le=100, description="得分，0-100分")
    feedback: str = Field(..., description="详细的反馈意见")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议")
    explanation: Optional[str] = Field(None, description="解题思路或解析")


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
    "questionGeneration": {
        "request": QuestionGenerationRequestData,
        "response": QuestionGenerationResponseData,
    },
    "knowledgeToMarkdown": {
        "request": KnowledgeToMarkdownRequestData,
        "response": KnowledgeToMarkdownResponseData,
    },
    "studentDialogue": {
        "request": DialogueRequestData,
        "response": DialogueResponseData,
    },
    "exerciseGeneration": {
        "request": ExerciseGenerationRequestData,
        "response": ExerciseGenerationResponseData,
    },
    "answerCorrection": {
        "request": DialogueRequestData,  # 重用DialogueRequestData，因为接口格式一致
        "response": AnswerCorrectionResponseData,
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


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取JSON对象
    
    Args:
        text: 可能包含JSON的文本
        
    Returns:
        提取的JSON对象，如果未找到则返回None
    """
    # 尝试直接解析整个文本
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试查找JSON对象的开始和结束位置
    start_idx = text.find('{')
    if start_idx == -1:
        return None
    
    # 找到可能的JSON对象
    brace_count = 0
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                # 找到完整的JSON对象
                try:
                    json_text = text[start_idx:i+1]
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    # 继续查找下一个可能的JSON对象
                    continue
    
    # 如果没有找到有效的JSON对象，返回None
    return None


# ==============================================================================
# 响应格式化和转换 (Response Formatting and Conversion)
# ==============================================================================

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


def format_question_generation_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    尝试将n8n返回的数据格式化为符合QuestionGenerationResponseData要求的结构
    
    Args:
        data: n8n返回的原始数据
        
    Returns:
        格式化后的数据，符合QuestionGenerationResponseData结构
    
    Raises:
        N8nResponseError: 如果无法格式化数据
    """
    logger.info("正在格式化问题生成响应数据")
    
    # 情况1: 如果n8n返回的是带有answer字段的对象
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        answer_text = data['answer']
        logger.info(f"检测到带有answer字段的响应，尝试从中提取JSON。文本长度: {len(answer_text)}")
        
        # 尝试从answer中提取JSON
        extracted_json = extract_json_from_text(answer_text)
        if extracted_json:
            logger.info("成功从answer字段中提取JSON结构")
            data = extracted_json
    
    # 情况2: 如果收到的是包含output字段的响应
    if isinstance(data, dict) and 'output' in data and isinstance(data['output'], str):
        text_output = data['output']
        logger.info(f"收到包含output字段的响应，尝试提取JSON。文本长度: {len(text_output)}")
        
        # 尝试从文本中提取JSON
        extracted_json = extract_json_from_text(text_output)
        if extracted_json:
            logger.info("成功从output字段中提取JSON结构")
            data = extracted_json
    
    # 情况3: 检查数据是否已经符合期望的结构
    if isinstance(data, dict) and 'questions' in data and isinstance(data['questions'], list):
        logger.info("数据结构已符合期望格式")
        
        # 应用格式化规则 - 导入需要在这里添加
        try:
            # 导入问题格式化工具
            from ai_services.services.question_format import QuestionFormatter
            
            # 格式化问题
            logger.info("应用问题格式化规则")
            formatter = QuestionFormatter()
            data['questions'] = formatter.format_questions(data['questions'])
            
            logger.info(f"成功格式化 {len(data['questions'])} 道问题")
        except Exception as e:
            logger.warning(f"应用问题格式化规则时出错: {str(e)}")
            # 错误不应阻止返回，继续使用原始数据
        
        return data
    
    # 尝试创建一个基本的兼容结构
    try:
        # 如果数据本身是带有code blocks的字符串
        if isinstance(data, str):
            extracted_json = extract_json_from_text(data)
            if extracted_json:
                logger.info("成功从字符串响应中提取JSON结构")
                data = extracted_json
        
        # 如果缺少questions字段，但有其他可能的字段
        if 'questions' not in data and 'items' in data and isinstance(data['items'], list):
            logger.info("从items字段构建questions列表")
            data['questions'] = data['items']
        
        # 最后检查结构是否完整
        if isinstance(data, dict) and 'questions' in data and isinstance(data['questions'], list):
            # 应用格式化规则 - 导入需要在这里添加
            try:
                # 导入问题格式化工具
                from ai_services.services.question_format import QuestionFormatter
                
                # 格式化问题
                logger.info("应用问题格式化规则")
                formatter = QuestionFormatter()
                data['questions'] = formatter.format_questions(data['questions'])
                
                logger.info(f"成功格式化 {len(data['questions'])} 道问题")
            except Exception as e:
                logger.warning(f"应用问题格式化规则时出错: {str(e)}")
                # 错误不应阻止返回，继续使用原始数据
            
            return data
        
        # 如果仍然不符合结构，抛出错误
        logger.error(f"无法格式化问题生成响应: {str(data)[:200]}...")
        raise N8nResponseError(
            message="问题生成响应格式无效",
            status_code=400,
            error_data={"error": "无法解析AI响应为有效的问题列表"}
        )
        
    except Exception as e:
        logger.exception("格式化问题生成响应时出错")
        raise N8nResponseError(
            message=f"格式化问题生成响应时出错: {str(e)}",
            status_code=500
        )


def format_knowledge_to_markdown_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    尝试将n8n返回的数据格式化为符合KnowledgeToMarkdownResponseData要求的结构
    
    Args:
        data: n8n返回的原始数据
        
    Returns:
        格式化后的数据，符合KnowledgeToMarkdownResponseData结构
    
    Raises:
        N8nResponseError: 如果无法格式化数据
    """
    logger.info("正在格式化知识点到Markdown转换响应数据")
    
    # 情况1: 如果n8n返回的是带有answer字段的对象
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        markdown_content = data['answer']
        logger.info(f"从answer字段中提取Markdown内容，长度: {len(markdown_content)}")
        return {"markdown": markdown_content}
    
    # 情况2: 如果收到的是包含output字段的响应
    if isinstance(data, dict) and 'output' in data and isinstance(data['output'], str):
        markdown_content = data['output']
        logger.info(f"从output字段中提取Markdown内容，长度: {len(markdown_content)}")
        return {"markdown": markdown_content}
    
    # 情况3: 如果返回的数据已经包含markdown字段
    if isinstance(data, dict) and 'markdown' in data and isinstance(data['markdown'], str):
        logger.info("数据结构已符合期望格式")
        return data
    
    # 尝试从文本中提取Markdown
    if isinstance(data, str):
        logger.info(f"直接使用字符串响应作为Markdown内容，长度: {len(data)}")
        return {"markdown": data}
    
    # 如果无法识别格式，抛出异常
    logger.error(f"无法格式化知识点到Markdown转换响应: {str(data)[:200]}...")
    raise N8nResponseError(
        message="无法识别AI服务返回的Markdown内容格式",
        error_data=data
    )


def format_student_dialogue_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    尝试将n8n返回的数据格式化为符合DialogueResponseData要求的结构
    
    Args:
        data: n8n返回的原始数据
        
    Returns:
        格式化后的数据，符合DialogueResponseData结构
    
    Raises:
        N8nResponseError: 如果无法格式化数据
    """
    logger.info("正在格式化学生对话响应数据")
    
    # 情况1: 如果n8n返回的是带有answer字段的对象
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        answer_text = data['answer']
        logger.info(f"检测到带有answer字段的响应，长度: {len(answer_text)}")
        
        # 尝试从answer中提取JSON
        extracted_json = extract_json_from_text(answer_text)
        if extracted_json and isinstance(extracted_json, dict) and 'answer' in extracted_json:
            logger.info("成功从answer字段中提取完整JSON结构")
            return extracted_json
        else:
            # 创建基本响应结构
            return {
                "answer": answer_text,
                "resources": [],
                "follow_up_questions": []
            }
    
    # 情况2: 如果收到的是包含output字段的响应
    if isinstance(data, dict) and 'output' in data and isinstance(data['output'], str):
        output_text = data['output']
        logger.info(f"检测到带有output字段的响应，长度: {len(output_text)}")
        
        # 尝试从output中提取JSON
        extracted_json = extract_json_from_text(output_text)
        if extracted_json and isinstance(extracted_json, dict) and 'answer' in extracted_json:
            logger.info("成功从output字段中提取完整JSON结构")
            return extracted_json
        else:
            # 创建基本响应结构
            return {
                "answer": output_text,
                "resources": [],
                "follow_up_questions": []
            }
    
    # 情况3: 如果返回的数据已包含answer/resources等字段
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        logger.info("数据结构已包含基本字段")
        
        # 确保包含所有必要字段
        if 'resources' not in data or not isinstance(data['resources'], list):
            data['resources'] = []
        if 'follow_up_questions' not in data or not isinstance(data['follow_up_questions'], list):
            data['follow_up_questions'] = []
            
        return data
    
    # 情况4: 如果数据是字符串
    if isinstance(data, str):
        logger.info(f"收到的是纯文本响应，长度: {len(data)}")
        
        # 尝试从字符串中提取JSON
        extracted_json = extract_json_from_text(data)
        if extracted_json and isinstance(extracted_json, dict) and 'answer' in extracted_json:
            logger.info("成功从文本响应中提取完整JSON结构")
            return extracted_json
        else:
            # 创建基本响应结构
            return {
                "answer": data,
                "resources": [],
                "follow_up_questions": []
            }
    
    # 如果无法识别格式，抛出异常
    logger.error(f"无法格式化学生对话响应: {str(data)[:200]}...")
    raise N8nResponseError(
        message="无法识别AI服务返回的对话内容格式",
        error_data=data
    )


def format_exercise_generation_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    尝试将n8n返回的练习题生成数据格式化为符合ExerciseGenerationResponseData要求的结构
    
    Args:
        data: n8n返回的原始数据
        
    Returns:
        格式化后的数据，符合ExerciseGenerationResponseData结构
    
    Raises:
        N8nResponseError: 如果无法格式化数据
    """
    logger.info("正在格式化练习题生成响应数据")
    
    # 提取会话ID，如果存在的话
    session_id = None
    if isinstance(data, dict) and 'sessionId' in data:
        session_id = data['sessionId']
    
    # 情况1: 如果n8n返回的是带有answer字段的对象（常见于某些模型的返回格式）
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        answer_text = data['answer']
        logger.info(f"检测到带有answer字段的响应，尝试解析练习题。文本长度: {len(answer_text)}")
        
        # 尝试从answer中提取JSON
        extracted_json = extract_json_from_text(answer_text)
        if extracted_json and 'questions' in extracted_json:
            logger.info("成功从answer字段中提取JSON结构")
            # 确保包含session_id
            if session_id and 'session_id' not in extracted_json:
                extracted_json['session_id'] = session_id
            return extracted_json
        
        # 如果不是JSON格式，尝试解析文本格式的练习题
        try:
            # 解析文本格式的练习题
            questions = parse_exercise_text(answer_text)
            logger.info(f"成功从文本中解析出 {len(questions)} 道练习题")
            
            result = {
                "questions": questions,
                "session_id": session_id or str(uuid.uuid4())  # 如果没有会话ID，生成一个新的
            }
            return result
        except Exception as e:
            logger.warning(f"解析练习题文本时出错: {str(e)}")
            # 继续尝试其他格式
    
    # 情况2: 如果收到的是包含output字段的响应
    if isinstance(data, dict) and 'output' in data and isinstance(data['output'], str):
        text_output = data['output']
        logger.info(f"收到包含output字段的响应，尝试解析练习题。文本长度: {len(text_output)}")
        
        # 尝试从文本中提取JSON
        extracted_json = extract_json_from_text(text_output)
        if extracted_json and 'questions' in extracted_json:
            logger.info("成功从output字段中提取JSON结构")
            # 确保包含session_id
            if session_id and 'session_id' not in extracted_json:
                extracted_json['session_id'] = session_id
            return extracted_json
        
        # 如果不是JSON格式，尝试解析文本格式的练习题
        try:
            # 解析文本格式的练习题
            questions = parse_exercise_text(text_output)
            logger.info(f"成功从文本中解析出 {len(questions)} 道练习题")
            
            result = {
                "questions": questions,
                "session_id": session_id or str(uuid.uuid4())  # 如果没有会话ID，生成一个新的
            }
            return result
        except Exception as e:
            logger.warning(f"解析练习题文本时出错: {str(e)}")
            # 继续尝试其他格式
    
    # 情况3: 检查数据是否已经符合期望的结构
    if isinstance(data, dict) and 'questions' in data and isinstance(data['questions'], list):
        logger.info("数据结构已符合期望格式")
        
        # 确保包含session_id
        if 'session_id' not in data:
            data['session_id'] = session_id or str(uuid.uuid4())
        
        return data
    
    # 情况4: 如果数据是字符串
    if isinstance(data, str):
        logger.info(f"收到的是纯文本响应，尝试解析练习题。长度: {len(data)}")
        
        # 尝试从字符串中提取JSON
        extracted_json = extract_json_from_text(data)
        if extracted_json and 'questions' in extracted_json:
            logger.info("成功从文本响应中提取完整JSON结构")
            # 确保包含session_id
            if session_id and 'session_id' not in extracted_json:
                extracted_json['session_id'] = session_id
            return extracted_json
        
        # 如果不是JSON格式，尝试解析文本格式的练习题
        try:
            # 解析文本格式的练习题
            questions = parse_exercise_text(data)
            logger.info(f"成功从文本中解析出 {len(questions)} 道练习题")
            
            result = {
                "questions": questions,
                "session_id": session_id or str(uuid.uuid4())  # 如果没有会话ID，生成一个新的
            }
            return result
        except Exception as e:
            logger.warning(f"解析练习题文本时出错: {str(e)}")
            # 继续尝试其他格式
    
    # 如果无法识别格式，抛出异常
    error_msg = f"无法格式化练习题生成响应: {str(data)[:200]}..."
    logger.error(error_msg)
    raise N8nResponseError(
        message="无法解析AI服务返回的练习题数据",
        error_data=data
    )

def parse_exercise_text(text: str) -> List[Dict[str, Any]]:
    """
    从文本中解析练习题
    
    Args:
        text: 包含练习题的文本
        
    Returns:
        解析后的练习题列表
    """
    questions = []
    
    # 检查文本是否包含练习题的关键词
    if "题目" not in text and "选项" not in text and "答案" not in text:
        raise ValueError("文本不包含练习题")
    
    # 尝试识别题目分隔符
    separators = ["---", "===", "###", "\n\n", "\n"]
    separator = None
    for sep in separators:
        if sep in text:
            separator = sep
            break
    
    if not separator:
        # 如果没有明显的分隔符，假设只有一道题目
        questions.append(parse_single_exercise(text))
    else:
        # 按分隔符拆分文本
        sections = text.split(separator)
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # 检查这个部分是否包含练习题的关键词
            if ("题目" in section or "问题" in section) and ("选项" in section or "答案" in section):
                try:
                    question = parse_single_exercise(section)
                    questions.append(question)
                except Exception as e:
                    logger.warning(f"解析题目时出错: {str(e)}, 部分文本: {section[:100]}...")
    
    # 如果没有解析出任何题目，尝试作为一个整体解析
    if not questions:
        try:
            questions.append(parse_single_exercise(text))
        except Exception as e:
            logger.warning(f"作为整体解析题目时出错: {str(e)}")
            raise ValueError("无法从文本中解析出练习题")
    
    return questions

def parse_single_exercise(text: str) -> Dict[str, Any]:
    """
    解析单个练习题
    
    Args:
        text: 包含单个练习题的文本
        
    Returns:
        解析后的练习题
    """
    # 默认值
    question = {
        "title": "练习题",
        "content": "",
        "type": "single_choice",  # 修改为下划线格式
        "difficulty": 3,
        "answer_template": [],
        "knowledge_point_id": None
    }
    
    # 提取题目内容
    content_match = re.search(r"题目[:：]?\s*(.*?)(?=选项|标准答案|答案|解析|$)", text, re.DOTALL)
    if content_match:
        question["content"] = content_match.group(1).strip()
        # 从内容中提取一个简短的标题
        title_text = question["content"].split("\n")[0][:50]
        question["title"] = title_text
    else:
        # 尝试其他可能的格式
        content_match = re.search(r"(?:^|\n)([^选项|标准答案|答案|解析]*?)(?=选项|标准答案|答案|解析|$)", text, re.DOTALL)
        if content_match:
            question["content"] = content_match.group(1).strip()
            title_text = question["content"].split("\n")[0][:50]
            question["title"] = title_text
    
    # 确定题目类型
    if "单选" in text or "选择一项" in text:
        question["type"] = "single_choice"  # 修改为下划线格式
    elif "多选" in text or "选择多项" in text:
        question["type"] = "multiple_choice"  # 修改为下划线格式
    elif "填空" in text:
        question["type"] = "fill_in"  # 修改为下划线格式
    elif "简答" in text or "解答" in text:
        question["type"] = "short_answer"  # 修改为下划线格式
    elif "编程" in text or "代码" in text:
        question["type"] = "programming"  # 保持一致性
    
    # 提取选项
    options_match = re.search(r"选项[:：]?\s*(.*?)(?=标准答案|答案|解析|$)", text, re.DOTALL)
    if options_match:
        options_text = options_match.group(1).strip()
        # 尝试匹配常见的选项格式: A. 选项内容 或 A) 选项内容 或 A、选项内容
        options = re.findall(r"([A-Z][\.、\)]\s*)(.*?)(?=[A-Z][\.、\)]|$)", options_text, re.DOTALL)
        if options:
            question["answer_template"] = [option[1].strip() for option in options]
        else:
            # 如果无法识别选项格式，直接使用整个选项文本
            question["answer_template"] = [options_text]
    
    # 提取难度
    difficulty_match = re.search(r"难度[:：]?\s*(\d+)", text)
    if difficulty_match:
        try:
            difficulty = int(difficulty_match.group(1))
            if 1 <= difficulty <= 5:
                question["difficulty"] = difficulty
        except ValueError:
            pass
    
    return question

# 修改parse_response函数，添加对exerciseGeneration任务类型的特殊处理
def parse_response(task_type: str, data: Dict[str, Any]) -> BaseModel:
    """
    解析和验证任务响应数据
    
    Args:
        task_type: 任务类型字符串
        data: 要解析的响应数据
        
    Returns:
        一个已验证的Pydantic模型实例
        
    Raises:
        N8nResponseError: 如果任务类型无效或数据验证失败
    """
    task_format = get_task_format(task_type)
    if not task_format:
        raise N8nResponseError(f"不支持的任务类型: {task_type}")
        
    response_model = task_format.get("response")
    if not response_model:
        raise N8nResponseError(f"任务类型 '{task_type}' 未定义响应模型")
    
    # 针对不同任务类型进行特定处理
    try:
        if task_type == "courseGeneration":
            formatted_data = format_course_generation_response(data)
        elif task_type == "questionGeneration":
            formatted_data = format_question_generation_response(data)
        elif task_type == "knowledgeToMarkdown":
            formatted_data = format_knowledge_to_markdown_response(data)
        elif task_type == "studentDialogue":
            formatted_data = format_student_dialogue_response(data)
        elif task_type == "exerciseGeneration":
            formatted_data = format_exercise_generation_response(data)
        elif task_type == "answerCorrection":
            formatted_data = format_answer_correction_response(data)
        elif task_type == "ragAI":
            # ragAI任务响应数据特殊处理
            if isinstance(data, dict) and "answer" in data:
                # 尝试解析sources（如果存在）
                sources = []
                if "sources" in data and isinstance(data["sources"], list):
                    sources = data["sources"]
                formatted_data = {
                    "answer": data["answer"],
                    "sources": sources
                }
            else:
                # 如果不是预期格式，返回一个简单响应
                formatted_data = {
                    "answer": str(data) if isinstance(data, str) else json.dumps(data),
                    "sources": []
                }
        else:
            # 默认情况，尝试原样使用数据
            formatted_data = data
    except Exception as e:
        # 捕获格式化过程中的所有异常
        logger.exception(f"格式化响应数据时出错: {str(e)}")
        raise N8nResponseError(
            message=f"格式化'{task_type}'任务响应数据时出错: {str(e)}",
            error_data=data
        )
    
    # 验证格式化后的数据
    try:
        model_instance = response_model(**formatted_data)
        return model_instance
    except ValidationError as e:
        # 捕获Pydantic验证错误
        logger.error(f"响应数据验证失败: {e.json()}")
        raise N8nResponseError(
            message=f"'{task_type}'任务响应数据验证失败",
            error_detail=e.json(),
            error_data=formatted_data,
            validation_errors=e.errors()
        )


def format_answer_correction_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    尝试将n8n返回的答案校正数据格式化为符合AnswerCorrectionResponseData要求的结构
    
    Args:
        data: n8n返回的原始数据
        
    Returns:
        格式化后的数据，符合AnswerCorrectionResponseData结构
    
    Raises:
        N8nResponseError: 如果无法格式化数据
    """
    logger.info("正在格式化答案校正响应数据")
    
    # 情况1: 如果n8n返回的是带有answer字段的对象
    if isinstance(data, dict) and 'answer' in data and isinstance(data['answer'], str):
        answer_text = data['answer']
        logger.info(f"检测到带有answer字段的响应，长度: {len(answer_text)}")
        
        # 尝试从answer中提取JSON
        extracted_json = extract_json_from_text(answer_text)
        if extracted_json and isinstance(extracted_json, dict):
            if 'is_correct' in extracted_json and 'score' in extracted_json and 'feedback' in extracted_json:
                logger.info("成功从answer字段中提取完整JSON结构")
                # 确保所有必要字段存在
                extracted_json['is_correct'] = bool(extracted_json.get('is_correct', False))
                extracted_json['score'] = float(extracted_json.get('score', 0))
                extracted_json['feedback'] = str(extracted_json.get('feedback', ''))
                
                # 处理可选字段
                if 'improvement_suggestions' not in extracted_json:
                    extracted_json['improvement_suggestions'] = None
                if 'explanation' not in extracted_json:
                    extracted_json['explanation'] = None
                    
                return extracted_json
        
        # 如果不是结构化JSON，尝试解析纯文本答案
        try:
            logger.info("尝试从纯文本中提取答案校正信息")
            
            # 提取得分 - 通常格式为"得分：XX分"或"Score: XX"
            score_match = re.search(r'(?:得分|分数|评分|Score)[：:]\s*(\d+(?:\.\d+)?)', answer_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 0.0
            
            # 提取正确性 - 查找常见的表示正确或错误的词语
            correct_patterns = ['正确', '对', '完全正确', '没有错误', 'correct', 'right']
            incorrect_patterns = ['错误', '不正确', '有误', '不完全正确', 'incorrect', 'wrong']
            
            is_correct = False
            for pattern in correct_patterns:
                if pattern in answer_text.lower() and all(neg not in answer_text.lower() for neg in ['不'+p for p in correct_patterns]):
                    is_correct = True
                    break
            for pattern in incorrect_patterns:
                if pattern in answer_text.lower():
                    is_correct = False
                    break
            
            # 尝试提取反馈部分 - 通常在"反馈"或"Feedback"之后
            feedback_match = re.search(r'(?:反馈|意见|建议|Feedback)[：:]\s*(.*?)(?=(?:改进建议|解析|$))', answer_text, re.IGNORECASE | re.DOTALL)
            feedback = feedback_match.group(1).strip() if feedback_match else answer_text
            
            # 尝试提取改进建议 - 通常在"改进建议"之后
            improvement_match = re.search(r'(?:改进建议|改进|建议|Suggestions)[：:]\s*(.*?)(?=(?:解析|$))', answer_text, re.IGNORECASE | re.DOTALL)
            improvement = improvement_match.group(1).strip() if improvement_match else None
            
            # 尝试提取解析 - 通常在"解析"之后
            explanation_match = re.search(r'(?:解析|解题思路|思路|解释|Explanation)[：:]\s*(.*?)(?=$)', answer_text, re.IGNORECASE | re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else None
            
            return {
                "is_correct": is_correct,
                "score": min(max(score, 0), 100),  # 确保分数在0-100之间
                "feedback": feedback,
                "improvement_suggestions": improvement,
                "explanation": explanation
            }
        except Exception as e:
            logger.warning(f"从纯文本解析答案校正信息失败: {str(e)}")
            # 创建基本响应结构
            return {
                "is_correct": False,
                "score": 0,
                "feedback": answer_text,
                "improvement_suggestions": None,
                "explanation": None
            }
    
    # 情况2: 如果收到的是包含output字段的响应
    if isinstance(data, dict) and 'output' in data and isinstance(data['output'], str):
        output_text = data['output']
        logger.info(f"检测到带有output字段的响应，长度: {len(output_text)}")
        
        # 处理方法与answer字段相同
        extracted_json = extract_json_from_text(output_text)
        if extracted_json and isinstance(extracted_json, dict):
            if 'is_correct' in extracted_json and 'score' in extracted_json and 'feedback' in extracted_json:
                logger.info("成功从output字段中提取完整JSON结构")
                # 确保所有必要字段存在
                extracted_json['is_correct'] = bool(extracted_json.get('is_correct', False))
                extracted_json['score'] = float(extracted_json.get('score', 0))
                extracted_json['feedback'] = str(extracted_json.get('feedback', ''))
                
                # 处理可选字段
                if 'improvement_suggestions' not in extracted_json:
                    extracted_json['improvement_suggestions'] = None
                if 'explanation' not in extracted_json:
                    extracted_json['explanation'] = None
                    
                return extracted_json
        
        # 如果不是JSON，按照处理answer字段的方法处理
        return format_answer_correction_response({"answer": output_text})
    
    # 情况3: 如果数据结构已经包含所需字段
    if isinstance(data, dict) and 'is_correct' in data and 'score' in data and 'feedback' in data:
        logger.info("数据结构已包含基本字段")
        
        # 确保字段类型正确
        data['is_correct'] = bool(data.get('is_correct', False))
        data['score'] = float(data.get('score', 0))
        data['feedback'] = str(data.get('feedback', ''))
        
        # 处理可选字段
        if 'improvement_suggestions' not in data:
            data['improvement_suggestions'] = None
        if 'explanation' not in data:
            data['explanation'] = None
            
        return data
    
    # 情况4: 如果数据是字符串
    if isinstance(data, str):
        logger.info(f"收到的是纯文本响应，长度: {len(data)}")
        
        # 尝试从字符串中提取JSON
        extracted_json = extract_json_from_text(data)
        if extracted_json and isinstance(extracted_json, dict):
            if 'is_correct' in extracted_json and 'score' in extracted_json and 'feedback' in extracted_json:
                logger.info("成功从文本响应中提取完整JSON结构")
                # 确保所有必要字段存在
                extracted_json['is_correct'] = bool(extracted_json.get('is_correct', False))
                extracted_json['score'] = float(extracted_json.get('score', 0))
                extracted_json['feedback'] = str(extracted_json.get('feedback', ''))
                
                # 处理可选字段
                if 'improvement_suggestions' not in extracted_json:
                    extracted_json['improvement_suggestions'] = None
                if 'explanation' not in extracted_json:
                    extracted_json['explanation'] = None
                    
                return extracted_json
        
        # 如果不是JSON，按照处理answer字段的方法处理
        return format_answer_correction_response({"answer": data})
    
    # 如果无法识别格式，抛出异常
    logger.error(f"无法格式化答案校正响应: {str(data)[:200]}...")
    raise N8nResponseError(
        message="无法识别AI服务返回的答案校正内容格式",
        error_data=data
    )


def parse_single_exercise(text: str) -> Dict[str, Any]:
    """
    从文本中解析单个练习题
    
    Args:
        text: 包含一个练习题的文本
        
    Returns:
        解析后的练习题
    """
    # 默认值
    question = {
        "title": "练习题",
        "content": "",
        "type": "single_choice",  # 修改为下划线格式
        "difficulty": 3,
        "answer_template": [],
        "knowledge_point_id": None
    }
    
    # 提取题目内容
    content_match = re.search(r"题目[:：]?\s*(.*?)(?=选项|标准答案|答案|解析|$)", text, re.DOTALL)
    if content_match:
        question["content"] = content_match.group(1).strip()
        # 从内容中提取一个简短的标题
        title_text = question["content"].split("\n")[0][:50]
        question["title"] = title_text
    else:
        # 尝试其他可能的格式
        content_match = re.search(r"(?:^|\n)([^选项|标准答案|答案|解析]*?)(?=选项|标准答案|答案|解析|$)", text, re.DOTALL)
        if content_match:
            question["content"] = content_match.group(1).strip()
            title_text = question["content"].split("\n")[0][:50]
            question["title"] = title_text
    
    # 确定题目类型
    if "单选" in text or "选择一项" in text:
        question["type"] = "single_choice"  # 修改为下划线格式
    elif "多选" in text or "选择多项" in text:
        question["type"] = "multiple_choice"  # 修改为下划线格式
    elif "填空" in text:
        question["type"] = "fill_in"  # 修改为下划线格式
    elif "简答" in text or "解答" in text:
        question["type"] = "short_answer"  # 修改为下划线格式
    elif "编程" in text or "代码" in text:
        question["type"] = "programming"  # 保持一致性
    
    # 提取选项
    options_match = re.search(r"选项[:：]?\s*(.*?)(?=标准答案|答案|解析|$)", text, re.DOTALL)
    if options_match:
        options_text = options_match.group(1).strip()
        # 尝试匹配常见的选项格式: A. 选项内容 或 A) 选项内容 或 A、选项内容
        options = re.findall(r"([A-Z][\.、\)]\s*)(.*?)(?=[A-Z][\.、\)]|$)", options_text, re.DOTALL)
        if options:
            question["answer_template"] = [option[1].strip() for option in options]
        else:
            # 如果无法识别选项格式，直接使用整个选项文本
            question["answer_template"] = [options_text]
    
    # 提取难度
    difficulty_match = re.search(r"难度[:：]?\s*(\d+)", text)
    if difficulty_match:
        try:
            difficulty = int(difficulty_match.group(1))
            if 1 <= difficulty <= 5:
                question["difficulty"] = difficulty
        except ValueError:
            pass
    
    return question 