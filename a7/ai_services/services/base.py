"""
基础AI服务接口模块

定义了AI服务层的抽象接口和通用基类
"""

import abc
from typing import Dict, Any, Optional, Union


class AIService(abc.ABC):
    """AI服务基础抽象接口类"""
    
    @abc.abstractmethod
    async def process_task(self, task_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI任务的抽象方法
        
        Args:
            task_type: 任务类型
            data: 任务输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
    
    @abc.abstractmethod
    def process_task_sync(self, task_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步处理AI任务的抽象方法
        
        Args:
            task_type: 任务类型
            data: 任务输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass


class WebhookServiceInterface(AIService):
    """基于Webhook的AI服务接口"""
    
    @abc.abstractmethod
    async def send_webhook_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送Webhook请求的抽象方法
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        pass
    
    @abc.abstractmethod
    def send_webhook_request_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步发送Webhook请求的抽象方法
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        pass 