"""
n8n Webhook 请求/响应格式定义模块

使用Pydantic定义标准化的数据结构，用于验证和构建与n8n服务交互的数据。
"""

from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, List, Optional

from .exceptions import N8nInvalidRequestError, N8nResponseError


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
    sources: List[RagAISource] = Field(default_factory=list, description="回答所依据的来源列表")


# ==============================================================================
# 任务格式注册与管理 (Task Format Registry)
# ==============================================================================

# 定义一个任务格式注册表，用于存储不同任务类型的请求和响应模型
TASK_FORMATS: Dict[str, Dict[str, Any]] = {
    "ragAI": {
        "request": RagAIRequestData,
        "response": RagAIResponseData,
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

    try:
        validated_model = response_model.model_validate(data)
        return validated_model
    except ValidationError as e:
        # 将Pydantic的验证错误包装为我们的自定义响应异常
        raise N8nResponseError(
            message=f"任务 '{task_type}' 的响应数据格式无效",
            validation_errors=e.errors()
        ) 