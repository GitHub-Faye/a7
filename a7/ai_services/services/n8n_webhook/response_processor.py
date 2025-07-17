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
        
        # 打印原始响应类型和结构
        logger.info(f"process_response接收到的原始响应类型: {type(raw_response)}")
        
        # 检查原始响应中是否包含sessionId和sources
        if isinstance(raw_response, dict):
            logger.info(f"原始响应键: {list(raw_response.keys())}")
            
            if 'sessionId' in raw_response:
                logger.info(f"原始响应中包含sessionId: {raw_response['sessionId']}")
            else:
                logger.info("原始响应中不包含sessionId")
                
            if 'sources' in raw_response:
                logger.info(f"原始响应中包含sources类型: {type(raw_response['sources'])}")
                logger.info(f"原始响应中包含sources: {raw_response['sources']}")
            else:
                logger.info("原始响应中不包含sources")
        elif isinstance(raw_response, list) and len(raw_response) > 0:
            logger.info("原始响应是列表")
            first_item = raw_response[0]
            if isinstance(first_item, dict):
                logger.info(f"列表第一项键: {list(first_item.keys())}")
                
                if 'sessionId' in first_item:
                    logger.info(f"列表第一项中包含sessionId: {first_item['sessionId']}")
                else:
                    logger.info("列表第一项中不包含sessionId")
                    
                if 'sources' in first_item:
                    logger.info(f"列表第一项中包含sources类型: {type(first_item['sources'])}")
                    logger.info(f"列表第一项中包含sources: {first_item['sources']}")
                else:
                    logger.info("列表第一项中不包含sources")
        else:
            logger.info(f"原始响应既不是字典也不是列表，类型为: {type(raw_response)}")
        
        try:
            # 根据任务类型选择相应的处理方法
            if task_type == "studentDialogue":
                result = format_student_dialogue_response(raw_response)
            elif task_type == "questionGeneration":
                result = format_question_generation_response(raw_response)
            elif task_type == "exerciseGeneration":
                result = format_exercise_generation_response(raw_response)
            elif task_type == "answerCorrection":
                result = format_answer_correction_response(raw_response)
            elif task_type == "courseGeneration":
                result = format_course_generation_response(raw_response)
            elif task_type == "knowledgeToMarkdown":
                result = format_knowledge_to_markdown_response(raw_response)
            elif task_type == "ragAI":
                result = ResponseProcessor._process_rag_ai_response(raw_response)
            else:
                # 对于未知任务类型，尝试通用处理
                result = ResponseProcessor._process_generic_response(raw_response)
                
            # 打印格式化后的响应结构
            logger.info(f"格式化后的响应类型: {type(result)}")
            if isinstance(result, dict):
                logger.info(f"格式化后的响应键: {list(result.keys())}")
                
                if 'sessionId' in result:
                    logger.info(f"格式化后的响应中包含sessionId: {result['sessionId']}")
                else:
                    logger.info("格式化后的响应中不包含sessionId")
                    
                if 'sources' in result:
                    logger.info(f"格式化后的响应中包含sources长度: {len(result['sources'])}")
                else:
                    logger.info("格式化后的响应中不包含sources")
            
            return result
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