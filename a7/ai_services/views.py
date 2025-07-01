from django.shortcuts import render

# Create your views here.

"""
AI服务API视图模块
"""

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .services.n8n_webhook.client import N8nWebhookClient
from .services.n8n_webhook.exceptions import N8nWebhookError, N8nInvalidRequestError
from .models import WebhookConfig
from .api_response import create_api_response
from .services.knowledge_converter import create_course_with_knowledge_points


class N8nWebhookAPIView(views.APIView):
    """n8n Webhook API接口视图"""
    permission_classes = [AllowAny]  # 允许所有请求访问，无需验证权限
    
    def post(self, request, *args, **kwargs):
        """处理POST请求，将请求转发到n8n webhook"""
        try:
            # 获取请求数据
            data = request.data
            task_type = data.get('task_type')
            task_data = data.get('data', {})
            
            # 验证任务类型
            if not task_type:
                return create_api_response(
                    success=False,
                    error_code="MISSING_PARAMETER",
                    message="缺少必要参数: task_type",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取webhook配置（可以基于请求中的标识或默认配置）
            webhook_id = data.get('webhook_id')
            webhook_config = None
            
            if webhook_id:
                try:
                    webhook_config = WebhookConfig.objects.get(id=webhook_id, active=True)
                except WebhookConfig.DoesNotExist:
                    return create_api_response(
                        success=False,
                        error_code="INVALID_WEBHOOK_ID",
                        message=f"找不到ID为 {webhook_id} 的活跃Webhook配置",
                        status_code=status.HTTP_404_NOT_FOUND
                    )
            
            # 创建客户端实例并发送请求
            client = N8nWebhookClient(webhook_config=webhook_config)
            result = client.process_ai_task_sync(task_type, task_data)
            
            # 如果是课程生成任务，则在数据库中创建课程和知识点
            if task_type == 'courseGeneration':
                course = create_course_with_knowledge_points(result, user=request.user)
                # 返回新创建的课程信息，而不是原始的n8n响应
                response_data = {
                    'course_id': course.id,
                    'title': course.title,
                    'message': '课程已成功创建'
                }
                return create_api_response(
                    success=True, 
                    data=response_data,
                    message="课程创建成功",
                    status_code=status.HTTP_201_CREATED  # 使用 201 表示资源已创建
                )

            # 对于其他任务，返回原始结果
            return create_api_response(
                success=True, 
                data=result, 
                message="任务处理成功",
                status_code=status.HTTP_200_OK
            )
            
        except N8nInvalidRequestError as e:
            # 处理无效请求数据异常
            return create_api_response(
                success=False,
                error_code="INVALID_REQUEST_DATA",
                message=str(e),
                status_code=e.status_code,
                details=e.validation_errors
            )
            
        except N8nWebhookError as e:
            # 处理n8n webhook相关的其他异常
            return create_api_response(
                success=False,
                error_code="WEBHOOK_PROCESSING_ERROR",
                message=str(e),
                status_code=e.status_code
            )
            
        except Exception as e:
            # 处理其他所有未捕获的异常
            return create_api_response(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message=f"处理请求时发生未知服务器错误: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
