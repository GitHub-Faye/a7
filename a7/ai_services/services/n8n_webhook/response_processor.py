"""
响应处理器模块

提供统一的响应处理机制，将AI服务的原始响应转换为标准格式
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from .formats import (
    parse_ai_response,
    extract_structured_data_from_text,
    extract_sources_from_text,
    extract_json_from_text,
    extract_correction_data_from_text,
    format_student_dialogue_response,
    format_question_generation_response,
    format_exercise_generation_response,
    format_answer_correction_response,
    format_course_generation_response,
    format_knowledge_to_markdown_response,
)
from .exceptions import N8nResponseError
from .logger import logger


class ResponseProcessor:
    """
    响应处理器类
    
    提供统一的方法来处理不同类型AI服务的响应，确保输出格式一致
    """
    
    @staticmethod
    def process_response(task_type: str, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI服务的原始响应，转换为标准格式
        
        Args:
            task_type: AI任务类型
            raw_response: 原始响应数据
            
        Returns:
            Dict[str, Any]: 标准化的响应数据
            
        Raises:
            N8nResponseError: 如果响应处理失败
        """
        logger.info(f"处理{task_type}任务的响应")
        
        try:
            # 根据任务类型选择相应的处理方法
            if task_type == "studentDialogue":
                return format_student_dialogue_response(raw_response)
            elif task_type == "questionGeneration":
                return format_question_generation_response(raw_response)
            elif task_type == "exerciseGeneration":
                return format_exercise_generation_response(raw_response)
            elif task_type == "answerCorrection":
                return format_answer_correction_response(raw_response)
            elif task_type == "courseGeneration":
                return format_course_generation_response(raw_response)
            elif task_type == "knowledgeToMarkdown":
                return format_knowledge_to_markdown_response(raw_response)
            elif task_type == "ragAI":
                return ResponseProcessor._process_rag_ai_response(raw_response)
            else:
                # 对于未知任务类型，尝试通用处理
                return ResponseProcessor._process_generic_response(raw_response)
        except Exception as e:
            logger.error(f"处理{task_type}任务响应时出错: {str(e)}")
            raise N8nResponseError(
                message=f"处理{task_type}任务响应失败: {str(e)}",
                error_data=raw_response
            )
    
    @staticmethod
    def _process_rag_ai_response(raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理RAG AI响应
        
        Args:
            raw_response: 原始响应数据
            
        Returns:
            Dict[str, Any]: 标准化的RAG AI响应
        """
        # 从响应中提取answer和sources文本
        answer_text, sources_text = parse_ai_response(raw_response)
        
        # 从sources文本中提取知识来源引用
        sources_data = extract_sources_from_text(sources_text) if sources_text else []
        
        # 构建响应数据
        return {
            "answer": answer_text,
            "sources": sources_data
        }
    
    @staticmethod
    def _process_generic_response(raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        通用响应处理方法
        
        Args:
            raw_response: 原始响应数据
            
        Returns:
            Dict[str, Any]: 尽可能标准化的响应数据
        """
        # 尝试从响应中提取answer和sources
        answer_text, sources_text = parse_ai_response(raw_response)
        
        # 尝试从answer中提取结构化数据
        structured_data = extract_structured_data_from_text(answer_text)
        
        # 从sources文本中提取知识来源引用
        sources_data = extract_sources_from_text(sources_text) if sources_text else []
        
        # 构建基本响应结构
        response_data = {
            "answer": structured_data.get("answer", answer_text),
            "sources": sources_data
        }
        
        # 添加其他可能的字段
        if "resources" in structured_data:
            response_data["resources"] = structured_data["resources"]
        
        if "follow_up_questions" in structured_data:
            response_data["follow_up_questions"] = structured_data["follow_up_questions"]
        
        return response_data


# 导出便捷函数
def process_response(task_type: str, raw_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理AI服务的原始响应，转换为标准格式
    
    Args:
        task_type: AI任务类型
        raw_response: 原始响应数据
        
    Returns:
        Dict[str, Any]: 标准化的响应数据
        
    Raises:
        N8nResponseError: 如果响应处理失败
    """
    return ResponseProcessor.process_response(task_type, raw_response) 