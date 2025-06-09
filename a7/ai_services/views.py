from django.shortcuts import render

# Create your views here.

"""
AI服务API视图模块
"""

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services.n8n_webhook.client import N8nWebhookClient
from .services.n8n_webhook.exceptions import N8nWebhookError
from .models import WebhookConfig


class N8nWebhookAPIView(views.APIView):
    """n8n Webhook API接口视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """处理POST请求，将请求转发到n8n webhook"""
        try:
            # 获取请求数据
            data = request.data
            task_type = data.get('task_type')
            task_data = data.get('data', {})
            
            # 验证任务类型
            if not task_type:
                return Response(
                    {"error": "缺少必要参数: task_type"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取webhook配置（可以基于请求中的标识或默认配置）
            webhook_id = data.get('webhook_id')
            webhook_config = None
            
            if webhook_id:
                try:
                    webhook_config = WebhookConfig.objects.get(id=webhook_id, active=True)
                except WebhookConfig.DoesNotExist:
                    return Response(
                        {"error": f"找不到ID为 {webhook_id} 的活跃Webhook配置"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # 创建客户端实例并发送请求
            client = N8nWebhookClient(webhook_config=webhook_config)
            result = client.process_ai_task_sync(task_type, task_data)
            
            return Response(result)
            
        except N8nWebhookError as e:
            # 处理n8n webhook异常
            return Response(
                {"error": str(e)}, 
                status=e.status_code
            )
            
        except Exception as e:
            # 处理其他异常
            return Response(
                {"error": f"处理请求时发生错误: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
