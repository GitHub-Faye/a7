"""
AI服务视图模块
"""

import logging
import uuid
from typing import Dict, Any

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from django.conf import settings

from courses.models import Course, KnowledgePoint
from courses.serializers import (
    CourseGenerationSerializer, 
    QuestionGenerationSerializer,
    StudentDialogueSerializer
)
from .services.n8n_webhook.client import N8nWebhookClient
from .services.n8n_webhook.exceptions import N8nWebhookError
from .api_response import create_api_response

logger = logging.getLogger(__name__)


class CourseContentGenerationViewSet(viewsets.ViewSet):
    """课程内容生成API视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """处理课程内容生成请求"""
        serializer = CourseContentGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 准备请求数据
            course_data = {
                "course_name": serializer.validated_data["course_name"],
                "course_description": serializer.validated_data["course_description"],
                "chapter_count": serializer.validated_data["chapter_count"],
                "subject": serializer.validated_data["subject"],
                "grade_level": serializer.validated_data["grade_level"],
                "additional_requirements": serializer.validated_data.get("additional_requirements", ""),
                # n8n格式要求
                "chatInput": f"Generate course content for {serializer.validated_data['course_name']}",
                "sessionId": str(uuid.uuid4())
            }
            
            # 调用n8n客户端
            client = N8nWebhookClient()
            result = client.generate_course_content_sync(course_data)
            
            return Response({
                "course": result["course"],
                "knowledge_points": result["knowledge_points"]
            }, status=status.HTTP_200_OK)
            
        except N8nWebhookError as e:
            logger.error(f"课程内容生成失败: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"课程内容生成处理异常: {str(e)}")
            return Response(
                {"error": f"处理课程内容生成请求时出错: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionGenerationViewSet(viewsets.ViewSet):
    """问题生成API视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """处理问题生成请求"""
        serializer = QuestionGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 获取知识点数据
            knowledge_point_ids = serializer.validated_data["knowledge_point_ids"]
            knowledge_points = KnowledgePoint.objects.filter(id__in=knowledge_point_ids)
            
            if not knowledge_points.exists():
                return Response(
                    {"error": "未找到指定的知识点"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 构建知识点内容字符串
            knowledge_content = ""
            for kp in knowledge_points:
                knowledge_content += f"知识点 {kp.id}: {kp.title}\n{kp.content}\n\n"
            
            # 准备请求数据
            question_data = {
                "knowledge_point_ids": knowledge_point_ids,
                "question_types": serializer.validated_data["question_types"],
                "quantity": serializer.validated_data["quantity"],
                "difficulty": serializer.validated_data.get("difficulty"),
                # n8n格式要求
                "chatInput": f"Generate {serializer.validated_data['quantity']} questions based on the following knowledge points:\n{knowledge_content}",
                "sessionId": str(uuid.uuid4())
            }
            
            # 调用n8n客户端
            client = N8nWebhookClient()
            result = client.generate_questions_sync(question_data)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except N8nWebhookError as e:
            logger.error(f"问题生成失败: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"问题生成处理异常: {str(e)}")
            return Response(
                {"error": f"处理问题生成请求时出错: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentDialogueViewSet(viewsets.ViewSet):
    """学生助手对话API视图集，处理学生查询并提供AI回复"""
    permission_classes = [permissions.AllowAny]  # 学生可无需认证使用
    
    def create(self, request, *args, **kwargs):
        """处理学生提问并返回AI响应"""
        serializer = StudentDialogueSerializer(data=request.data)
        
        # 手动处理验证错误，以保留字段错误信息
        if not serializer.is_valid():
            return create_api_response(
                success=False,
                message="请求参数验证失败",
                error_code="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 准备会话ID，如果请求中没有提供则生成新的
            session_id = serializer.validated_data.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 准备请求数据 - 注意：n8n服务期望chatInput而不是query
            dialogue_data = {
                # 将query映射到chatInput
                "chatInput": serializer.validated_data["query"],
                "sessionId": session_id,
                # 可选：如果需要传递上下文
                "context": serializer.validated_data.get("context", {})
            }
            
            # 调用n8n客户端
            client = N8nWebhookClient()
            result = client.dialogue_with_student_sync(dialogue_data)
            
            # 在响应中包含会话ID，便于客户端进行后续对话
            result["session_id"] = session_id
            
            # 使用标准化响应格式
            return create_api_response(
                success=True,
                data=result,
                message="对话请求处理成功",
                status_code=status.HTTP_200_OK
            )
            
        except N8nWebhookError as e:
            logger.error(f"学生对话处理失败: {str(e)}")
            return create_api_response(
                success=False,
                message=str(e),
                error_code="N8N_WEBHOOK_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"学生对话处理异常: {str(e)}")
            return create_api_response(
                success=False,
                message=f"处理学生对话请求时出错: {str(e)}",
                error_code="INTERNAL_SERVER_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
