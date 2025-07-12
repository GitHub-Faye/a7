"""
AI服务视图模块
"""

import logging
import uuid
from typing import Dict, Any
import json

from rest_framework import viewsets, status, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from django.conf import settings

from courses.models import Course, KnowledgePoint, Exercise
from courses.serializers import (
    CourseGenerationSerializer, 
    QuestionGenerationSerializer,
    StudentDialogueSerializer
)
from .services.n8n_webhook.client import N8nWebhookClient
from .services.n8n_webhook.exceptions import N8nWebhookError
from .api_response import create_api_response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class StudentDialogueViewSet(viewsets.ViewSet):
    """学生助手对话API视图集，处理学生查询并提供AI回复"""
    permission_classes = [permissions.AllowAny]  # 学生可无需认证使用
    
    @swagger_auto_schema(
        operation_summary="学生助手对话",
        operation_description="处理学生提出的问题并返回AI生成的回复",
        request_body=StudentDialogueSerializer,
        responses={
            200: openapi.Response(
                description="成功处理对话请求",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "answer": "AI生成的回答内容",
                            "session_id": "会话ID"
                        },
                        "message": "对话请求处理成功"
                    }
                }
            ),
            400: "请求参数验证失败",
            500: "服务器内部错误"
        }
    )
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


class ExerciseGenerationSerializer(serializers.Serializer):
    """练习题生成请求的序列化器"""
    query = serializers.CharField(
        required=True,
        help_text="生成练习题的查询或主题"
    )
    knowledge_point_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        help_text="可选的知识点ID列表"
    )
    question_types = serializers.ListField(
        child=serializers.ChoiceField(choices=Exercise.EXERCISE_TYPES),
        required=False,
        help_text="问题类型列表，如果不提供则生成多种类型"
    )
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=10,
        default=3,
        help_text="生成练习题的数量，默认3道"
    )
    difficulty = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        help_text="问题难度(1-5)"
    )
    session_id = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="会话ID，用于跟踪多轮交互"
    )
    
    def validate_knowledge_point_ids(self, value):
        """验证知识点ID是否存在"""
        if value:
            for kp_id in value:
                try:
                    KnowledgePoint.objects.get(id=kp_id)
                except KnowledgePoint.DoesNotExist:
                    raise serializers.ValidationError(f"ID为{kp_id}的知识点不存在")
        return value


class ExerciseGenerationViewSet(viewsets.ViewSet):
    """练习题生成API视图集，生成练习题但不保存到数据库"""
    permission_classes = [permissions.AllowAny]  # 允许匿名访问，便于学生使用
    
    @swagger_auto_schema(
        operation_summary="生成练习题",
        operation_description="基于输入的查询或知识点生成练习题，支持指定数量、类型和难度",
        request_body=ExerciseGenerationSerializer,
        responses={
            200: openapi.Response(
                description="成功生成练习题",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "exercises": [
                                {
                                    "title": "练习题标题",
                                    "content": "练习题内容",
                                    "type": "类型",
                                    "difficulty": 3,
                                    "answer_template": ["选项A", "选项B"]
                                }
                            ],
                            "session_id": "会话ID"
                        },
                        "message": "练习题生成成功"
                    }
                }
            ),
            400: "请求参数验证失败或知识点不存在",
            500: "服务器内部错误"
        }
    )
    def create(self, request, *args, **kwargs):
        """处理练习题生成请求"""
        serializer = ExerciseGenerationSerializer(data=request.data)
        
        # 手动处理验证错误，以提供友好的错误信息
        if not serializer.is_valid():
            return create_api_response(
                success=False,
                message="请求参数验证失败",
                error_code="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取并准备请求数据
            query = serializer.validated_data["query"]
            knowledge_point_ids = serializer.validated_data.get("knowledge_point_ids", [])
            question_types = serializer.validated_data.get("question_types", [])
            quantity = serializer.validated_data.get("quantity", 3)
            difficulty = serializer.validated_data.get("difficulty")
            
            # 准备会话ID，如果请求中没有提供则生成新的
            session_id = serializer.validated_data.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 如果提供了知识点ID，获取知识点内容
            knowledge_content = ""
            if knowledge_point_ids:
                knowledge_points = KnowledgePoint.objects.filter(id__in=knowledge_point_ids)
                for kp in knowledge_points:
                    knowledge_content += f"知识点 {kp.id}: {kp.title}\n{kp.content}\n\n"
            
            # 准备请求数据
            exercise_data = {
                "query": query,
                "knowledge_content": knowledge_content if knowledge_content else None,
                "question_types": question_types if question_types else None,
                "quantity": quantity,
                "difficulty": difficulty,
                # n8n格式要求
                "chatInput": f"生成{quantity}道练习题，内容关于: {query}" + 
                             (f"\n基于以下知识点内容:\n{knowledge_content}" if knowledge_content else "") +
                             (f"\n题型要求: {', '.join(question_types)}" if question_types else "") +
                             (f"\n难度级别: {difficulty}/5" if difficulty else ""),
                "sessionId": session_id
            }
            
            # 调用n8n客户端
            client = N8nWebhookClient()
            result = client.generate_exercises_sync(exercise_data)
            
            # 处理返回的练习题数据
            if 'questions' not in result:
                raise ValueError("API返回的数据缺少练习题内容")
            
            # 确保使用请求中的会话ID，而不是响应中可能返回的不同ID
            # 返回处理后的响应
            return create_api_response(
                success=True,
                data={
                    "exercises": result["questions"],
                    "session_id": session_id  # 使用请求中的会话ID，确保一致性
                },
                message="练习题生成成功",
                status_code=status.HTTP_200_OK
            )
            
        except N8nWebhookError as e:
            logger.error(f"练习题生成失败: {str(e)}")
            return create_api_response(
                success=False,
                message=str(e),
                error_code="N8N_WEBHOOK_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"练习题生成处理异常: {str(e)}")
            return create_api_response(
                success=False,
                message=f"处理练习题生成请求时出错: {str(e)}",
                error_code="INTERNAL_SERVER_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentAnswerCorrectionSerializer(serializers.Serializer):
    """学生答案校正请求的序列化器"""
    exercise_id = serializers.IntegerField(
        required=True, 
        help_text="需要校正的练习题ID"
    )
    student_answer = serializers.CharField(
        required=True,
        help_text="学生提交的答案内容"
    )
    session_id = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="会话ID，用于跟踪上下文"
    )
    
    def validate_exercise_id(self, value):
        """验证练习题ID是否存在"""
        try:
            Exercise.objects.get(id=value)
        except Exercise.DoesNotExist:
            raise serializers.ValidationError(f"ID为{value}的练习题不存在")
        return value


class StudentAnswerCorrectionViewSet(viewsets.ViewSet):
    """学生答案校正API视图集，评估学生答案但不直接保存到数据库"""
    permission_classes = [permissions.AllowAny]  # 允许匿名访问，便于学生使用
    
    @swagger_auto_schema(
        operation_summary="评估学生答案",
        operation_description="对指定练习题的学生答案进行评估，返回正确性、得分和反馈信息",
        request_body=StudentAnswerCorrectionSerializer,
        responses={
            200: openapi.Response(
                description="成功评估答案",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "is_correct": True,
                            "score": 95,
                            "feedback": "评价反馈",
                            "improvement_suggestions": "改进建议",
                            "explanation": "解题思路",
                            "session_id": "会话ID"
                        },
                        "message": "答案评估成功"
                    }
                }
            ),
            400: "请求参数验证失败",
            404: "练习题不存在",
            500: "服务器内部错误"
        }
    )
    def create(self, request, *args, **kwargs):
        """处理答案校正请求"""
        serializer = StudentAnswerCorrectionSerializer(data=request.data)
        
        # 手动处理验证错误，以提供友好的错误信息
        if not serializer.is_valid():
            return create_api_response(
                success=False,
                message="请求参数验证失败",
                error_code="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取练习题和学生答案
            exercise_id = serializer.validated_data["exercise_id"]
            student_answer = serializer.validated_data["student_answer"]
            
            # 获取练习题详情
            exercise = Exercise.objects.get(id=exercise_id)
            
            # 准备会话ID，如果请求中没有提供则生成新的
            session_id = serializer.validated_data.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 构建prompt，包含练习题信息和学生答案
            prompt = f"""请评估以下学生答案:

题目标题: {exercise.title}
题目类型: {dict(Exercise.EXERCISE_TYPES).get(exercise.type, exercise.type)}
题目内容: {exercise.content}
"""

            # 根据题目类型添加不同的信息
            if exercise.type in ['single_choice', 'multiple_choice'] and exercise.answer_template:
                # 添加选项信息
                try:
                    options = json.loads(exercise.answer_template) if isinstance(exercise.answer_template, str) else exercise.answer_template
                    if isinstance(options, list):
                        prompt += "\n选项:\n"
                        for i, option in enumerate(options):
                            prompt += f"{chr(65+i)}. {option}\n"
                        
                        # 特别说明多选题
                        if exercise.type == 'multiple_choice':
                            prompt += "\n注意：这是一道多选题，可以选择多个正确答案。学生的答案格式为逗号分隔的选项，如'A,C,D'。\n"
                except (json.JSONDecodeError, TypeError):
                    prompt += f"\n选项: {exercise.answer_template}\n"
            elif exercise.answer_template:
                # 对于其他类型，如果有答案模板，也一并提供
                prompt += f"\n参考答案模板: {exercise.answer_template}\n"
            
            # 添加学生答案
            prompt += f"\n学生答案: {student_answer}\n"
            
            # 添加评估指示
            prompt += """
请评估这个答案并提供:
1. 是否正确 (true/false)
2. 得分 (0-100)
3. 详细反馈
4. 改进建议
5. 解题思路或解析
"""

            # 根据题目类型添加特定的评估指导
            if exercise.type == 'multiple_choice':
                prompt += """
对于多选题，评分标准如下:
- 如果所有选项都正确选择且没有选择错误选项，则is_correct为true，得分为100分
- 如果部分正确（有些正确选项被选中，有些错误选项也被选中），则is_correct为false，但得分应该根据正确率给出（如50-80分）
- 如果完全错误，则is_correct为false，得分接近0分
"""

            prompt += """
请以JSON格式回复，包含以下字段:
{
    "is_correct": true或false,
    "score": 0-100之间的数字,
    "feedback": "详细反馈",
    "improvement_suggestions": "改进建议",
    "explanation": "解题思路或解析"
}
"""
            
            # 准备请求数据
            correction_data = {
                "chatInput": prompt,
                "sessionId": session_id
            }
            
            # 调用n8n客户端
            client = N8nWebhookClient()
            result = client.correct_student_answer_sync(correction_data)
            
            # 确保结果中包含会话ID
            result['session_id'] = session_id
            
            # 返回处理后的响应
            return create_api_response(
                success=True,
                data=result,
                message="答案评估成功",
                status_code=status.HTTP_200_OK
            )
            
        except N8nWebhookError as e:
            logger.error(f"答案校正失败: {str(e)}")
            return create_api_response(
                success=False,
                message=str(e),
                error_code="N8N_WEBHOOK_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(f"答案校正处理异常: {str(e)}")
            return create_api_response(
                success=False,
                message=f"处理答案校正请求时出错: {str(e)}",
                error_code="INTERNAL_SERVER_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
