"""
n8n Webhook客户端模块

实现了与n8n工作流程平台交互的客户端类
"""

import json
import time
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union

from django.conf import settings
from asgiref.sync import sync_to_async

from .exceptions import (
    N8nWebhookError,
    N8nConnectionError,
    N8nTimeoutError,
    N8nResponseError,
)
from ...models import WebhookConfig, WebhookCallLog

logger = logging.getLogger(__name__)


class N8nWebhookClient:
    """n8n Webhook客户端类，提供与n8n工作流程平台交互的方法"""

    def __init__(self, webhook_config: Optional[Union[WebhookConfig, Dict]] = None, timeout: int = 30):
        """
        初始化n8n Webhook客户端
        
        Args:
            webhook_config: Webhook配置对象或配置字典。如果为None，将使用默认配置
            timeout: 请求超时时间（秒）
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
        # 构建请求数据
        request_data = {
            "task_type": task_type,
            "data": task_data
        }
        
        # 发送请求并返回结果
        return await self.send_request(request_data)
    
    def process_ai_task_sync(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI任务请求（同步方法）
        
        Args:
            task_type: 任务类型，如'text_classification'、'text_generation'等
            task_data: 任务相关数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        return asyncio.run(self.process_ai_task(task_type, task_data)) 