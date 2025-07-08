import os
import logging
from django.http import FileResponse
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from . import convert_markdown_to_format
from .serializers import MarpConversionSerializer
from .exceptions import MarpServiceError
from .utils import get_mime_type, OutputFormat, DEFAULT_THEMES

# 创建logger
logger = logging.getLogger(__name__)


class MarpConversionView(views.APIView):
    """
    用于将Markdown内容转换为演示格式（PDF、PPTX、HTML、PNG）的API端点
    """
    # 根据项目设置，使用AllowAny权限
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="将Markdown内容转换为演示文档（PDF、PPTX、HTML、PNG）",
        request_body=MarpConversionSerializer,
        responses={
            200: openapi.Response(
                description="成功转换，返回文件",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: openapi.Response(
                description="无效的请求参数",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'error': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            415: openapi.Response(
                description="不支持的媒体类型",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                description="服务器内部错误",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        operation_summary="Markdown转演示文档",
        operation_id="convert_markdown",
        tags=["Marp服务"],
        manual_parameters=[
            openapi.Parameter(
                'Accept',
                openapi.IN_HEADER,
                description="接受的响应类型",
                type=openapi.TYPE_STRING,
                default="application/pdf, application/vnd.openxmlformats-officedocument.presentationml.presentation, text/html, image/png"
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        """处理POST请求，转换Markdown内容"""
        serializer = MarpConversionSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"无效的转换请求: {serializer.errors}")
            return Response(
                {"success": False, "error": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 提取验证后的数据
        content = serializer.validated_data['content']
        output_format = serializer.validated_data['format']
        theme = serializer.validated_data.get('theme')
        
        try:
            # 调用服务函数进行转换
            output_file = convert_markdown_to_format(
                content=content,
                output_format=output_format,
                theme=theme
            )
            
            # 获取文件名和MIME类型
            file_name = os.path.basename(output_file)
            mime_type = get_mime_type(output_format)
            
            # 创建文件响应
            response = FileResponse(
                open(output_file, 'rb'),
                content_type=mime_type,
                as_attachment=True,
                filename=f"presentation.{output_format}"
            )
            
            # 日志记录成功转换
            logger.info(f"成功将Markdown转换为{output_format}格式")
            
            return response
            
        except ValueError as e:
            # 处理验证错误
            logger.warning(f"格式验证错误: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
            
        except MarpServiceError as e:
            # 处理Marp服务错误
            logger.error(f"Marp服务错误: {str(e)}")
            return Response(
                {"success": False, "error": f"转换失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        except Exception as e:
            # 处理其他未预期的错误
            logger.exception(f"转换过程中发生未知错误: {str(e)}")
            return Response(
                {"success": False, "error": "服务器内部错误"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # 注意：convert_markdown_to_format函数内部已经处理了临时文件清理
            # 如果在此处需要额外清理，可以在这里添加
            pass