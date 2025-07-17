"""
n8n Webhook客户端模块

实现了与n8n工作流程平台交互的客户端类
"""

import json
import time
import logging
import aiohttp
import asyncio
import uuid
from typing import Dict, Any, Optional, Union, List

from django.conf import settings
from asgiref.sync import sync_to_async

from .exceptions import (
    N8nWebhookError,
    N8nConnectionError,
    N8nTimeoutError,
    N8nResponseError,
    N8nInvalidRequestError,
)
from .formats import validate_request_data, parse_response
from ...models import WebhookConfig, WebhookCallLog
from . import prompt_templates

logger = logging.getLogger(__name__)


class N8nWebhookClient:
    """n8n Webhook客户端类，提供与n8n工作流程平台交互的方法"""

    def __init__(self, webhook_config: Optional[Union[WebhookConfig, Dict]] = None, timeout: int = 300):
        """
        初始化n8n Webhook客户端
        
        Args:
            webhook_config: Webhook配置对象或配置字典。如果为None，将使用默认配置
            timeout: 请求超时时间（秒），默认为300秒（5分钟）
        """
        self.timeout = timeout
        self.webhook_config = None
        self.webhook_url = None
        self.headers = {}
        
        # 如果传入了webhook配置
        if webhook_config:
            if isinstance(webhook_config, WebhookConfig):
                self.webhook_config = webhook_config
                self.webhook_url = webhook_config.url
                self.headers = webhook_config.headers or {}
            elif isinstance(webhook_config, dict):
                self.webhook_url = webhook_config.get('url')
                self.headers = webhook_config.get('headers', {})
        
        # 默认情况下尝试从设置中获取
        if not self.webhook_url:
            self.webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', None)
            self.headers = getattr(settings, 'N8N_WEBHOOK_HEADERS', {})
            
        # 如果仍未设置webhook URL，则抛出异常
        if not self.webhook_url:
            raise ValueError("未提供n8n Webhook URL。请在webhook_config中提供或在settings中配置N8N_WEBHOOK_URL。")

    async def send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送异步请求到n8n Webhook
        
        Args:
            data: 要发送的数据
            
        Returns:
            Dict[str, Any]: n8n的响应数据
            
        Raises:
            N8nConnectionError: 连接错误
            N8nTimeoutError: 请求超时
            N8nResponseError: 响应错误
        """
        # 创建调用日志记录
        call_log = None
        start_time = time.time()
        
        if self.webhook_config:
            # 使用sync_to_async包装同步数据库操作
            create_log = sync_to_async(WebhookCallLog.objects.create)
            call_log = await create_log(
                webhook=self.webhook_config,
                request_data=data,
                status='pending'
            )
        
        try:
            # 超时设置
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.post(
                        self.webhook_url,
                        json=data,
                        headers=self.headers
                    ) as response:
                        # 计算执行时间
                        execution_time = time.time() - start_time
                        
                        # 尝试解析JSON响应
                        try:
                            response_data = await response.json()
                        except (json.JSONDecodeError, aiohttp.ContentTypeError):
                            # 如果无法解析JSON，获取文本响应
                            response_text = await response.text()
                            response_data = {"text": response_text}
                        
                        # 检查响应状态
                        if response.status >= 400:
                            error_msg = f"n8n Webhook请求失败: {response.status} {response.reason}"
                            # 更新调用日志
                            if call_log:
                                # 使用sync_to_async包装同步数据库操作
                                call_log.status = 'error'
                                call_log.response_data = response_data
                                call_log.error_message = error_msg
                                call_log.execution_time = execution_time
                                save_log = sync_to_async(call_log.save)
                                await save_log()
                                
                            raise N8nResponseError(
                                message=error_msg,
                                status_code=response.status,
                                response=response_data,
                                error_data=response_data
                            )
                        
                        # 更新调用日志
                        if call_log:
                            # 使用sync_to_async包装同步数据库操作
                            call_log.status = 'success'
                            call_log.response_data = response_data
                            call_log.execution_time = execution_time
                            save_log = sync_to_async(call_log.save)
                            await save_log()
                            
                        return response_data
                
                except asyncio.TimeoutError:
                    # 超时异常处理
                    error_msg = f"n8n Webhook请求超时: {self.timeout}秒"
                    logger.error(error_msg)
                    
                    # 更新调用日志
                    if call_log:
                        # 使用sync_to_async包装同步数据库操作
                        call_log.status = 'error'
                        call_log.error_message = error_msg
                        call_log.execution_time = time.time() - start_time
                        save_log = sync_to_async(call_log.save)
                        await save_log()
                        
                    raise N8nTimeoutError(message=error_msg)
                
                except (aiohttp.ClientError, aiohttp.ServerDisconnectedError) as e:
                    # 连接异常处理
                    error_msg = f"n8n Webhook连接错误: {str(e)}"
                    logger.error(error_msg)
                    
                    # 更新调用日志
                    if call_log:
                        # 使用sync_to_async包装同步数据库操作
                        call_log.status = 'error'
                        call_log.error_message = error_msg
                        call_log.execution_time = time.time() - start_time
                        save_log = sync_to_async(call_log.save)
                        await save_log()
                        
                    raise N8nConnectionError(message=error_msg)
                
        except Exception as e:
            # 捕获所有其他异常
            if not isinstance(e, N8nWebhookError):
                error_msg = f"n8n Webhook请求发生未知错误: {str(e)}"
                logger.exception(error_msg)
                
                # 更新调用日志
                if call_log:
                    # 使用sync_to_async包装同步数据库操作
                    call_log.status = 'error'
                    call_log.error_message = error_msg
                    call_log.execution_time = time.time() - start_time
                    save_log = sync_to_async(call_log.save)
                    await save_log()
                    
                # 包装为N8nWebhookError
                raise N8nWebhookError(message=error_msg) from e
            else:
                # 重新抛出N8nWebhookError类型的异常
                raise
    
    def send_request_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送同步请求到n8n Webhook（包装异步方法）
        
        Args:
            data: 要发送的数据
            
        Returns:
            Dict[str, Any]: n8n的响应数据
        """
        return asyncio.run(self.send_request(data))
    
    async def process_ai_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI任务请求
        
        Args:
            task_type: 任务类型，如'text_classification'、'text_generation'等
            task_data: 任务相关数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 1. 验证请求数据
        try:
            validated_data_model = validate_request_data(task_type, task_data)
            validated_data = validated_data_model.model_dump()
        except N8nInvalidRequestError as e:
            # 重新抛出验证错误
            raise e
        except Exception as e:
            # 包装其他异常为N8nInvalidRequestError
            raise N8nInvalidRequestError(str(e))
        
        # 2. 构建将发送到n8n的请求数据
        request_data = {
            "task_type": task_type,
            "data": validated_data
        }
        
        # 3. 发送请求并获取原始响应
        raw_response = await self.send_request(request_data)
        
        # 记录原始响应
        logger.info(f"从N8N接收到原始响应类型: {type(raw_response)}")
        if isinstance(raw_response, list) and len(raw_response) > 0:
            logger.info(f"原始响应是列表，长度: {len(raw_response)}")
            first_item = raw_response[0]
            if isinstance(first_item, dict):
                logger.info(f"原始响应列表第一项键: {list(first_item.keys())}")
                
                # 检查是否包含sessionId
                if 'sessionId' in first_item:
                    logger.info(f"原始响应中包含sessionId: {first_item['sessionId']}")
                    
                # 检查是否包含sources
                if 'sources' in first_item:
                    logger.info(f"原始响应中包含sources: {first_item['sources']}")
        elif isinstance(raw_response, dict):
            logger.info(f"原始响应是字典，键: {list(raw_response.keys())}")
            
            # 检查是否包含sessionId和sources
            if 'sessionId' in raw_response:
                logger.info(f"原始响应中包含sessionId: {raw_response['sessionId']}")
            if 'sources' in raw_response:
                logger.info(f"原始响应中包含sources: {raw_response['sources']}")
        
        # 4. 处理响应数据
        try:
            validated_response_model = parse_response(task_type, raw_response)
            return validated_response_model.model_dump()
        except Exception as e:
            logger.exception(f"处理响应时出错: {str(e)}")
            raise N8nResponseError(
                message=f"处理'{task_type}'任务响应失败: {str(e)}",
                error_data=raw_response
            )
    
    def process_ai_task_sync(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI任务请求（同步方法）
        
        Args:
            task_type: 任务类型，如'text_classification'、'text_generation'等
            task_data: 任务相关数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        logger.info("进入process_ai_task_sync方法")
        
        # 调试打印任务类型和数据
        logger.info(f"处理任务类型: {task_type}")
        
        # 检查task_data中的sessionId
        if 'sessionId' in task_data:
            logger.info(f"输入task_data中包含sessionId: {task_data['sessionId']}")
        else:
            logger.info("输入task_data中不包含sessionId")
        
        # 运行异步处理方法
        raw_result = asyncio.run(self.process_ai_task(task_type, task_data))
        
        # 调试输出raw_result类型和结构
        logger.info(f"process_ai_task返回的raw_result类型: {type(raw_result)}")
        if isinstance(raw_result, dict):
            logger.info(f"raw_result字典键: {list(raw_result.keys())}")
            if 'sessionId' in raw_result:
                logger.info(f"raw_result中包含sessionId: {raw_result['sessionId']}")
            else:
                logger.info("raw_result中不包含sessionId")
                
            if 'sources' in raw_result:
                logger.info(f"raw_result中包含sources类型: {type(raw_result['sources'])}")
                logger.info(f"raw_result中包含sources值: {raw_result['sources']}")
            else:
                logger.info("raw_result中不包含sources")
        elif isinstance(raw_result, list) and len(raw_result) > 0:
            logger.info(f"raw_result是列表，长度: {len(raw_result)}")
            first_item = raw_result[0]
            if isinstance(first_item, dict):
                logger.info(f"raw_result[0]的键: {list(first_item.keys())}")
                if 'sessionId' in first_item:
                    logger.info(f"raw_result[0]中包含sessionId: {first_item['sessionId']}")
                if 'sources' in first_item:
                    logger.info(f"raw_result[0]中包含sources: {first_item['sources']}")
        
        return raw_result
    
    async def generate_course_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成课程内容的便捷方法
        
        Args:
            request_data: 包含课程名称、描述等信息的请求数据
            
        Returns:
            Dict[str, Any]: 生成的课程内容
        """
        # 提取参数
        course_name = request_data.get("course_name", "")
        chapter_count = request_data.get("chapter_count", 5)
        course_description = request_data.get("course_description", "")
        subject = request_data.get("subject", "")
        grade_level = request_data.get("grade_level", "")
        additional_requirements = request_data.get("additional_requirements", "")
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 使用提示模板构建chatInput
        chat_input = prompt_templates.build_course_content_generation_prompt(
            course_name=course_name,
            chapter_count=chapter_count,
            course_description=course_description,
            subject=subject,
            grade_level=grade_level,
            additional_requirements=additional_requirements
        )
        
        # 构建请求数据 - 同时传递chatInput和必要参数
        task_data = {
            "course_name": course_name,
            "chapter_count": chapter_count,
            "course_description": course_description,
            "subject": subject,
            "grade_level": grade_level,
            "chatInput": chat_input,
            "sessionId": session_id
        }
        
        # 1. 验证请求数据
        validated_data_model = validate_request_data('courseGeneration', task_data)
        
        # 2. 构建将发送到n8n的请求数据
        request_data_to_send = {
            "task_type": 'courseGeneration',
            "data": validated_data_model.model_dump()
        }
        
        # 3. 发送请求并获取原始响应
        raw_response = await self.send_request(request_data_to_send)
        
        # 4. 处理嵌套响应格式 - 先提取answer、sources和sessionId
        if isinstance(raw_response, list) and len(raw_response) > 0 and 'response' in raw_response[0]:
            # 获取嵌套的响应内容
            nested_response = raw_response[0]['response']
            
            # 从响应体中提取数据
            if 'body' in nested_response and len(nested_response['body']) > 0:
                body_item = nested_response['body'][0]
                
                # 提取answer、sources和sessionId
                answer = body_item.get('answer', '')
                sources = body_item.get('sources', '')
                session_id = body_item.get('sessionId', session_id)
                
                # 构建格式化的响应
                formatted_response = {
                    'answer': answer,
                    'sources': sources,
                    'sessionId': session_id
                }
                
                # 处理响应数据
                validated_response_model = parse_response('courseGeneration', formatted_response)
                return validated_response_model.model_dump()
        
        # 如果没有找到嵌套格式，按照标准方式处理
        validated_response_model = parse_response('courseGeneration', raw_response)
        return validated_response_model.model_dump()
    
    def generate_course_content_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成课程内容的便捷方法（同步版本）
        
        Args:
            request_data: 包含课程名称、描述等信息的请求数据
            
        Returns:
            Dict[str, Any]: 生成的课程内容
        """
        # 提取参数
        course_name = request_data.get("course_name", "")
        chapter_count = request_data.get("chapter_count", 5)
        course_description = request_data.get("course_description", "")
        subject = request_data.get("subject", "计算机科学")  # 设置默认值，避免空字段
        grade_level = request_data.get("grade_level", "大学一年级")  # 设置默认值，避免空字段
        additional_requirements = request_data.get("additional_requirements", "")
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 使用提示模板构建chatInput
        chat_input = prompt_templates.build_course_content_generation_prompt(
            course_name=course_name,
            chapter_count=chapter_count,
            course_description=course_description,
            subject=subject,
            grade_level=grade_level,
            additional_requirements=additional_requirements
        )
        
        # 构建请求数据 - 包含所有必要参数
        task_data = {
            "course_name": course_name,
            "chapter_count": chapter_count,
            "course_description": course_description,
            "subject": subject, 
            "grade_level": grade_level,
            "additional_requirements": additional_requirements,
            "chatInput": chat_input,
            "sessionId": session_id
        }
        
        try:
            # 通过process_ai_task_sync处理请求
            logger.info("通过process_ai_task_sync处理课程生成请求")
            raw_result = self.process_ai_task_sync('courseGeneration', task_data)
            logger.info(f"process_ai_task_sync返回数据类型: {type(raw_result)}")
            
            # 提取并处理嵌套响应格式
            result = raw_result
            
            # 检查是否有嵌套的响应结构
            if isinstance(raw_result, dict) and 'response' in raw_result:
                logger.info("检测到嵌套响应结构")
                
                if 'body' in raw_result['response'] and isinstance(raw_result['response']['body'], list) and len(raw_result['response']['body']) > 0:
                    body_item = raw_result['response']['body'][0]
                    logger.info(f"响应body[0]结构: {list(body_item.keys()) if isinstance(body_item, dict) else type(body_item)}")
                    
                    if isinstance(body_item, dict):
                        # 提取answer和sources
                        if 'answer' in body_item:
                            answer = body_item['answer']
                            logger.info(f"从嵌套响应中提取answer，长度: {len(answer)}")
                            
                            # 提取sources
                            sources = ""
                            if 'sources' in body_item:
                                if isinstance(body_item['sources'], str):
                                    sources = body_item['sources']
                                elif isinstance(body_item['sources'], list):
                                    sources = json.dumps(body_item['sources'])
                                logger.info(f"从嵌套响应中提取sources，长度: {len(sources)}")
                            
                            # 构建格式化的响应
                            formatted_response = {
                                "answer": answer,
                                "sources": sources,
                                "sessionId": body_item.get('sessionId', session_id)
                            }
                            
                            # 尝试从answer中提取JSON格式的课程数据
                            import re
                            import json as json_module
                            
                            json_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', answer)
                            
                            if json_match:
                                try:
                                    json_str = json_match.group(1)
                                    logger.info(f"从嵌套响应中提取JSON字符串，长度: {len(json_str)}")
                                    course_data = json_module.loads(json_str)
                                    
                                    # 确保课程基本信息存在
                                    if 'course' in course_data and isinstance(course_data['course'], dict):
                                        # 强制使用请求中的课程名称作为title
                                        course_data['course']['title'] = course_name
                                        
                                        # 确保subject和grade_level不为空
                                        if not course_data['course'].get('subject'):
                                            course_data['course']['subject'] = subject
                                        if not course_data['course'].get('grade_level'):
                                            course_data['course']['grade_level'] = grade_level
                                    
                                    # 检查知识点标题长度
                                    if 'knowledge_points' in course_data and isinstance(course_data['knowledge_points'], list):
                                        for i, kp in enumerate(course_data['knowledge_points']):
                                            if isinstance(kp, dict) and 'title' in kp:
                                                title = kp['title']
                                                if len(title) > 100:
                                                    logger.warning(f"知识点标题过长，进行截断: '{title[:20]}...'")
                                                    course_data['knowledge_points'][i]['title'] = title[:97] + '...'
                                                    
                                                # 处理子知识点
                                                if 'children' in kp and isinstance(kp['children'], list):
                                                    for j, child in enumerate(kp['children']):
                                                        if isinstance(child, dict) and 'title' in child:
                                                            child_title = child['title']
                                                            if len(child_title) > 100:
                                                                logger.warning(f"子知识点标题过长，进行截断: '{child_title[:20]}...'")
                                                                course_data['knowledge_points'][i]['children'][j]['title'] = child_title[:97] + '...'
                                    
                                    # 更新answer字段为格式化的JSON
                                    formatted_response['answer'] = json_module.dumps(course_data)
                                    
                                    # 通过formats.py中的函数解析响应
                                    from .formats import parse_response
                                    validated_response_model = parse_response('courseGeneration', formatted_response)
                                    result = validated_response_model.model_dump()
                                    logger.info("成功从嵌套响应中提取并解析课程内容")
                                except Exception as json_error:
                                    logger.error(f"解析嵌套响应中的JSON失败: {str(json_error)}")
            
            # 调试输出结果结构
            if isinstance(result, dict):
                logger.info(f"最终结果结构: {list(result.keys())}")
                
                # 确保结果中course包含必要字段
                if 'course' in result and isinstance(result['course'], dict):
                    logger.info(f"课程字段: {list(result['course'].keys())}")
                    
                    # 强制使用请求中的课程名称作为title
                    result['course']['title'] = course_name
                    
                    # 强制使用请求中的课程描述
                    result['course']['description'] = course_description
                    
                    # 确保subject和grade_level不为空
                    if not result['course'].get('subject'):
                        result['course']['subject'] = subject
                    if not result['course'].get('grade_level'):
                        result['course']['grade_level'] = grade_level
                    
                    logger.info(f"课程标题: {result['course'].get('title')}")
                    logger.info(f"课程描述: {result['course'].get('description')}")
                
                # 检查知识点数量和标题
                if 'knowledge_points' in result and isinstance(result['knowledge_points'], list):
                    knowledge_points = result['knowledge_points']
                    logger.info(f"知识点数量: {len(knowledge_points)}")
                    
                    if knowledge_points:
                        first_kp = knowledge_points[0]
                        if isinstance(first_kp, dict) and 'title' in first_kp:
                            first_title = first_kp['title']
                            logger.info(f"第一个知识点标题: '{first_title}'，长度: {len(first_title)}")
                        
                        last_kp = knowledge_points[-1]
                        if isinstance(last_kp, dict) and 'title' in last_kp:
                            last_title = last_kp['title']
                            logger.info(f"最后一个知识点标题: '{last_title}'，长度: {len(last_title)}")
            
            return result
            
        except Exception as e:
            logger.error(f"生成课程内容时出错: {str(e)}")
            # 返回一个基本的响应结构
            return {
                "course": {
                    "title": course_name,  # 使用请求中的课程名称
                    "description": course_description,  # 使用请求中的课程描述
                    "subject": subject,
                    "grade_level": grade_level
                },
                "knowledge_points": []
            }
    
    async def generate_questions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成问题的便捷方法
        
        Args:
            request_data: 包含知识点ID、问题类型和数量等信息的请求数据
            
        Returns:
            Dict[str, Any]: 生成的问题列表
        """
        # 提取参数
        knowledge_point_ids = request_data.get("knowledge_point_ids", [])
        knowledge_points = request_data.get("knowledge_points", [])
        question_types = request_data.get("question_types", ["multiple_choice"])
        quantity = request_data.get("quantity", 5)
        difficulty = request_data.get("difficulty", 3)
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 如果客户端提供了chatInput，直接使用
        if "chatInput" in request_data and request_data["chatInput"]:
            chat_input = request_data["chatInput"]
        else:
            # 否则使用提示模板构建chatInput
            chat_input = prompt_templates.build_question_generation_prompt(
                knowledge_point_ids=knowledge_point_ids,
                knowledge_points=knowledge_points,
                question_types=question_types,
                quantity=quantity,
                difficulty=difficulty
            )
        
        # 传递所有必需参数给process_ai_task，而不仅仅是chatInput和sessionId
        return await self.process_ai_task('questionGeneration', {
            "knowledge_point_ids": knowledge_point_ids,
            "question_types": question_types,
            "quantity": quantity,
            "difficulty": difficulty,
            "chatInput": chat_input,
            "sessionId": session_id
        })
    
    def generate_questions_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成问题的便捷方法（同步版本）
        
        Args:
            request_data: 包含知识点ID、问题类型和数量等信息的请求数据
            
        Returns:
            Dict[str, Any]: 生成的问题列表
        """
        return asyncio.run(self.generate_questions(request_data))
    
    async def generate_markdown_from_knowledge(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从知识点数据生成Markdown的便捷方法
        
        Args:
            request_data: 包含知识点数据和配置选项的请求数据
            
        Returns:
            Dict[str, Any]: 包含生成Markdown的响应数据
        """
        # 提取参数
        knowledge_data = request_data.get("knowledge_data", {})
        title = request_data.get("title", "知识点演示")
        include_course_info = request_data.get("include_course_info", True)
        theme = request_data.get("theme", "default")
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 如果客户端提供了chatInput，直接使用
        if "chatInput" in request_data and request_data["chatInput"]:
            chat_input = request_data["chatInput"]
        else:
            # 否则使用提示模板构建chatInput
            chat_input = prompt_templates.build_knowledge_to_markdown_prompt(
                knowledge_data=knowledge_data,
                title=title,
                theme=theme,
                include_course_info=include_course_info
            )
        
        # 只传递chatInput和sessionId给n8n
        return await self.process_ai_task('knowledgeToMarkdown', {
            "chatInput": chat_input,
            "sessionId": session_id
        })
    
    def generate_markdown_from_knowledge_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从知识点数据生成Markdown的便捷方法（同步版本）
        
        Args:
            request_data: 包含知识点数据和配置选项的请求数据
            
        Returns:
            Dict[str, Any]: 包含生成Markdown的响应数据
        """
        return asyncio.run(self.generate_markdown_from_knowledge(request_data))
        
    async def dialogue_with_student(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理学生对话请求的便捷方法
        
        Args:
            request_data: 包含学生查询文本和会话ID的请求数据
            
        Returns:
            Dict[str, Any]: 包含AI助手回答的响应数据
        """
        # 提取参数
        query = request_data.get("query") or request_data.get("chatInput", "")
        context = request_data.get("context", {})
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 使用提示模板构建chatInput
        chat_input = prompt_templates.build_student_dialogue_prompt(query, context)
        
        # 只传递chatInput和sessionId给n8n
        return await self.process_ai_task('studentDialogue', {
            "chatInput": chat_input,
            "sessionId": session_id
        })
    
    def dialogue_with_student_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理学生对话请求的便捷方法（同步版本）
        
        Args:
            request_data: 包含学生查询文本和会话ID的请求数据
            
        Returns:
            Dict[str, Any]: 包含AI助手回答的响应数据
        """
        return asyncio.run(self.dialogue_with_student(request_data)) 
        
    async def generate_exercises(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成练习题（异步方法）
        
        Args:
            request_data: 请求数据，包含查询和生成参数
            
        Returns:
            Dict[str, Any]: 生成的练习题数据
        """
        # 提取参数
        query = request_data.get("query", "")
        knowledge_content = request_data.get("knowledge_content", "")
        question_types = request_data.get("question_types", [])
        quantity = request_data.get("quantity", 3)
        difficulty = request_data.get("difficulty")
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 如果客户端提供了chatInput，直接使用
        if "chatInput" in request_data and request_data["chatInput"]:
            chat_input = request_data["chatInput"]
        else:
            # 否则使用提示模板构建chatInput
            chat_input = prompt_templates.build_exercise_generation_prompt(
                query=query,
                knowledge_content=knowledge_content,
                question_types=question_types,
                quantity=quantity,
                difficulty=difficulty
            )
        
        # 只传递chatInput和sessionId给n8n
        return await self.process_ai_task("exerciseGeneration", {
            "chatInput": chat_input,
            "sessionId": session_id
        })

    def generate_exercises_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成练习题（同步方法）
        
        Args:
            request_data: 练习题生成任务的请求数据
            
        Returns:
            Dict[str, Any]: 生成的练习题数据
        """
        return asyncio.run(self.generate_exercises(request_data))
        
    async def correct_student_answer(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估和校正学生答案（异步方法）
        
        Args:
            request_data: 答案校正任务的请求数据，应包含:
                - exercise_content: 练习题内容
                - exercise_type: 练习题类型
                - reference_answer: 参考答案
                - student_answer: 学生答案
                - answer_template: 答案模板(可选)
                - sessionId: 会话ID，用于跟踪上下文
                
        Returns:
            Dict[str, Any]: 校正结果，包含正确性评估、得分、反馈等
        """
        # 提取参数
        exercise_content = request_data.get("exercise_content", "")
        exercise_type = request_data.get("exercise_type", "")
        reference_answer = request_data.get("reference_answer", "")
        student_answer = request_data.get("student_answer", "")
        answer_template = request_data.get("answer_template", None)
        session_id = request_data.get("sessionId", str(uuid.uuid4()))
        
        # 使用提示模板构建chatInput
        chat_input = prompt_templates.build_answer_correction_prompt(
            exercise_content=exercise_content,
            exercise_type=exercise_type,
            reference_answer=reference_answer,
            student_answer=student_answer,
            answer_template=answer_template
        )
        
        # 只传递chatInput和sessionId给n8n
        return await self.process_ai_task("answerCorrection", {
            "chatInput": chat_input,
            "sessionId": session_id
        })
        
    def correct_student_answer_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估和校正学生答案（同步方法）
        
        Args:
            request_data: 答案校正任务的请求数据
            
        Returns:
            Dict[str, Any]: 校正结果，包含正确性评估、得分、反馈等
        """
        return asyncio.run(self.correct_student_answer(request_data)) 