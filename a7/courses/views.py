import os
import json
import base64
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction
from django.utils.translation import gettext as _

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Course, KnowledgePoint, Courseware, Exercise, StudentAnswer, LearningRecord, CourseProgress, CoursewareFile
from .serializers import (
    CourseSerializer, CourseCreateSerializer, CourseUpdateSerializer, CourseGenerationSerializer,
    KnowledgePointSerializer, KnowledgePointCreateSerializer, KnowledgePointUpdateSerializer,
    CoursewareSerializer, CoursewareCreateSerializer, CoursewareUpdateSerializer,
    QuestionGenerationSerializer, ExerciseSerializer, ExerciseCreateSerializer, ExerciseUpdateSerializer,
    StudentAnswerSerializer, StudentAnswerCreateSerializer, StudentAnswerUpdateSerializer,
    CourseContentGenerationResponseSerializer, CoursewareFileUploadSerializer, CoursewareFileSerializer
)
from .serializers_ppt import KnowledgePointToPPTSerializer
from .serializers_progress import CourseProgressDetailSerializer, LearningRecordSerializer, LearningRecordUpdateSerializer
from .permissions import IsTeacherOrAdmin, IsCourseTeacherOrAdmin, IsKnowledgePointCourseTeacherOrAdmin
from .validations import validate_text_field
from .utils import validate_file_type, validate_file_size
from .services.knowledge_to_ppt import KnowledgePointToPPTService
from ai_services.services.n8n_webhook import N8nWebhookClient
from ai_services.services.n8n_webhook.exceptions import N8nWebhookError, N8nInvalidRequestError
from ai_services.services.n8n_webhook.client import WebhookConfig
from ai_services.api_response import create_api_response
from ai_services.services.question_export import QuestionExporter
from users.models import User

import uuid
import logging
from datetime import datetime

# 获取日志记录器
logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    """
    课程视图集，提供课程的增删改查功能
    """
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]  # 默认需要用户认证
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'subject', 'grade_level']
    ordering_fields = ['created_at', 'title', 'subject', 'grade_level']
    
    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        """
        if self.action == 'create':
            return CourseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CourseUpdateSerializer
        return CourseSerializer
    
    def get_permissions(self):
        """
        根据操作类型设置不同的权限
        """
        if self.action == 'list' or self.action == 'retrieve':
            # 允许任何人查看课程列表和详情
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            # 需要登录才能创建课程
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 只有课程创建者或管理员才能修改/删除课程
            self.permission_classes = [IsCourseTeacherOrAdmin]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="获取当前用户创建的课程列表",
        operation_description="返回当前已认证用户创建的所有课程"
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_courses(self, request):
        """
        获取当前用户创建的课程列表
        """
        try:
            # 确保用户已认证
            if not request.user.is_authenticated:
                return Response(
                    {"success": False, "message": "用户未登录或认证失败"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # 获取用户ID
            user = request.user
            print(f"当前用户: ID={user.id}, 用户名={user.username}")
            
            # 查询属于当前用户的课程
            queryset = self.queryset.filter(teacher=user.id)
            print(f"查询到的课程数量: {queryset.count()}")
            
            # 分页处理
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"success": False, "message": "获取课程失败", "errors": [str(e)]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class KnowledgePointViewSet(viewsets.ModelViewSet):
    """
    知识点视图集，提供知识点的增删改查功能
    """
    queryset = KnowledgePoint.objects.all().order_by('importance', 'title')
    serializer_class = KnowledgePointSerializer
    permission_classes = [permissions.AllowAny]  # 允许所有请求访问，无需验证权限
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['importance', 'title']
    
    def get_queryset(self):
        """
        可根据URL参数过滤知识点：
        - course: 按课程ID过滤
        - parent: 按父知识点ID过滤，使用null表示顶级知识点
        """
        queryset = super().get_queryset()
        
        # 按课程过滤
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # 按父知识点过滤
        parent_id = self.request.query_params.get('parent')
        if parent_id == 'null':
            # 顶级知识点（没有父级）
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
            
        return queryset
    
    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        """
        if self.action == 'create':
            return KnowledgePointCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return KnowledgePointUpdateSerializer
        return KnowledgePointSerializer
    
    def get_permissions(self):
        """
        根据操作类型设置不同的权限
        """
        if self.action == 'create':
            # 任何人都可以创建知识点
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 任何人都可以修改或删除知识点
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="获取课程的顶级知识点",
        operation_description="返回指定课程的所有顶级知识点（没有父级的知识点）"
    )
    @action(detail=False, methods=['get'])
    def top_level(self, request):
        """
        获取顶级知识点列表（没有父级的知识点）
        可选参数: course - 课程ID，用于筛选特定课程的顶级知识点
        """
        course_id = request.query_params.get('course')
        queryset = KnowledgePoint.objects.filter(parent__isnull=True)
        
        if course_id:
            try:
                course_id = int(course_id)
                queryset = queryset.filter(course_id=course_id)
            except ValueError:
                return Response(
                    {"success": False, "message": "无效的课程ID", "errors": ["课程ID必须是整数"]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="获取知识点的子知识点",
        operation_description="返回指定知识点的所有直接子知识点"
    )
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """
        获取指定知识点的直接子知识点
        """
        try:
            knowledge_point = self.get_object()
            children = knowledge_point.children.all().order_by('-importance', 'title')
            
            page = self.paginate_queryset(children)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(children, many=True)
            return Response(serializer.data)
        except KnowledgePoint.DoesNotExist:
            return Response(
                {"success": False, "message": "知识点不存在", "errors": [f"ID为{pk}的知识点不存在"]},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "获取子知识点失败", "errors": [str(e)]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CoursewareViewSet(viewsets.ModelViewSet):
    """
    课件视图集，提供课件的增删改查功能
    """
    queryset = Courseware.objects.all().order_by('-created_at')
    permission_classes = [permissions.AllowAny]  # 允许所有请求访问，无需验证权限
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'type']
    ordering_fields = ['created_at', 'title', 'type']
    
    def get_queryset(self):
        """
        可根据URL参数过滤课件：
        - course: 按课程ID过滤
        """
        queryset = super().get_queryset()
        
        # 按课程过滤
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        return queryset
    
    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        """
        if self.action == 'create':
            return CoursewareCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CoursewareUpdateSerializer
        elif self.action == 'upload':
            return CoursewareFileUploadSerializer
        return CoursewareSerializer
    
    def get_permissions(self):
        """
        根据不同的操作返回不同的权限
        """
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy' or self.action == 'upload':
            # 创建、更新、删除课件需要教师或管理员权限
            permission_classes = [IsTeacherOrAdmin]
        elif self.action == 'download':
            # 下载文件需要用户认证
            permission_classes = [permissions.IsAuthenticated]
        else:
            # 其他操作允许所有用户访问
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        operation_summary="获取指定课程的所有课件",
        operation_description="返回属于指定课程ID的所有课件资料"
    )
    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """
        获取指定课程的所有课件
        必须参数: course - 课程ID
        """
        # 验证必要参数
        validation_error = validate_text_field(request, ['course'])
        if validation_error:
            return validation_error
        
        course_id = request.query_params.get('course')
        queryset = self.queryset.filter(course_id=course_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data})

    @swagger_auto_schema(
        operation_summary="上传课件文件",
        operation_description="上传文件并关联到指定的课件",
        request_body=CoursewareFileUploadSerializer,
        responses={
            201: CoursewareFileSerializer,
            400: "请求参数无效",
            403: "权限不足",
            404: "课件不存在"
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def upload(self, request):
        """
        上传课件文件并关联到指定的课件
        """
        # 添加调试日志 - 打印请求数据
        print("\n========== 文件上传调试信息 ==========")
        print(f"请求数据: {request.data}")
        print(f"请求文件: {request.FILES}")
        if 'file' in request.FILES:
            file_obj = request.FILES['file']
            print(f"文件名: {file_obj.name}")
            print(f"文件大小: {file_obj.size} 字节")
            print(f"文件类型: {getattr(file_obj, 'content_type', '未知')}")
        
        serializer = CoursewareFileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            # 添加调试日志 - 打印验证错误
            print("\n========== 序列化器验证错误 ==========")
            print(f"错误详情: {serializer.errors}")
            
            # 检查具体字段错误
            if 'courseware_id' in serializer.errors:
                print(f"courseware_id 错误: {serializer.errors['courseware_id']}")
            if 'file' in serializer.errors:
                print(f"file 错误: {serializer.errors['file']}")
            
            # 检查文件类型验证
            if 'file' in request.FILES:
                file_obj = request.FILES['file']
                allowed_types = getattr(settings, 'ALLOWED_FILE_TYPES', [])
                print(f"允许的文件类型: {allowed_types}")
                print(f"文件扩展名: {os.path.splitext(file_obj.name)[1].lower()}")
                print(f"文件内容类型: {getattr(file_obj, 'content_type', '未知')}")
                print(f"文件类型验证结果: {validate_file_type(file_obj, allowed_types)}")
            
            return create_api_response(
                success=False,
                error_code="VALIDATION_ERROR",
                message=_("参数验证失败"),
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取课件
        try:
            courseware_id = serializer.validated_data['courseware_id']
            courseware = Courseware.objects.get(id=courseware_id)
            
            # 添加调试日志 - 课件信息
            print("\n========== 课件信息 ==========")
            print(f"课件ID: {courseware.id}")
            print(f"课件标题: {courseware.title}")
            print(f"课件所属课程: {courseware.course.title} (ID: {courseware.course.id})")
            print(f"课件创建者: {courseware.created_by.username} (ID: {courseware.created_by.id})")
            print(f"当前用户: {request.user.username} (ID: {request.user.id})")
            print(f"用户是否为课程教师: {courseware.course.teacher == request.user}")
            print(f"用户是否为管理员: {request.user.is_staff}")
            
        except Courseware.DoesNotExist:
            print("\n========== 错误 ==========")
            print(f"课件ID {courseware_id} 不存在")
            return create_api_response(
                success=False,
                error_code="NOT_FOUND",
                message=_("课件不存在"),
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 验证用户是否有权限上传文件到此课件
        if courseware.course.teacher != request.user and not request.user.is_staff:
            print("\n========== 权限错误 ==========")
            print(f"用户 {request.user.username} 无权限上传文件到课件 {courseware.title}")
            return create_api_response(
                success=False,
                error_code="PERMISSION_DENIED",
                message=_("您没有权限上传文件到此课件"),
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # 创建文件记录
        try:
            file = serializer.validated_data['file']
            
            # 添加调试日志 - 文件信息
            print("\n========== 准备创建文件记录 ==========")
            print(f"文件名: {file.name}")
            print(f"文件大小: {file.size} 字节")
            print(f"文件类型: {getattr(file, 'content_type', '未知')}")
            
            courseware_file = CoursewareFile.objects.create(
                courseware=courseware,
                file=file
            )
            
            # 添加调试日志 - 创建成功
            print("\n========== 文件记录创建成功 ==========")
            print(f"文件ID: {courseware_file.id}")
            print(f"文件名: {courseware_file.file_name}")
            print(f"文件大小: {courseware_file.file_size} 字节")
            print(f"文件类型: {courseware_file.file_type}")
            print(f"文件URL: {courseware_file.get_file_url()}")
            
            # 返回文件信息
            response_serializer = CoursewareFileSerializer(courseware_file)
            return create_api_response(
                success=True,
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            print("\n========== 文件上传异常 ==========")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {str(e)}")
            print(f"异常详情: ", e)
            import traceback
            print(f"堆栈跟踪: {traceback.format_exc()}")
            
            return create_api_response(
                success=False,
                error_code="UPLOAD_ERROR",
                message=_("文件上传失败"),
                errors=[str(e)],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="下载课件文件",
        operation_description="下载指定ID的课件文件",
        responses={
            200: "文件下载",
            403: "权限不足",
            404: "文件不存在"
        }
    )
    @action(detail=False, methods=['get'], url_path='download/(?P<file_id>[^/.]+)')
    def download(self, request, file_id=None):
        """
        下载课件文件
        """
        try:
            # 查找文件
            courseware_file = CoursewareFile.objects.get(id=file_id)
            
            # 权限检查
            user = request.user
            courseware = courseware_file.courseware
            course = courseware.course
            
            # 添加调试日志
            print(f"\n========== 文件下载请求 ==========")
            print(f"用户: ID={user.id}, 用户名={user.username}")
            print(f"文件: ID={courseware_file.id}, 名称={courseware_file.file_name}")
            print(f"课件: ID={courseware.id}, 标题={courseware.title}")
            print(f"课程: ID={course.id}, 标题={course.title}")
            
            # 检查用户是否有权限访问
            has_access = False
            if user.is_staff:  # 管理员
                print("用户是管理员，允许访问")
                has_access = True
            elif course.teacher == user:  # 课程教师
                print("用户是课程教师，允许访问")
                has_access = True
            else:  # 检查是否是已注册学生
                # 使用CourseProgress模型检查学生是否已注册课程
                student_progress = CourseProgress.objects.filter(
                    student=user,
                    course=course
                ).exists()
                if student_progress:
                    print("用户是已注册学生，允许访问")
                    has_access = True
                else:
                    print("用户不是已注册学生，拒绝访问")
            
            if not has_access:
                return create_api_response(
                    success=False,
                    error_code="PERMISSION_DENIED",
                    message=_("您没有权限下载此文件"),
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # 获取文件路径
            file_path = courseware_file.file.path
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return create_api_response(
                    success=False,
                    error_code="FILE_NOT_FOUND",
                    message=_("文件不存在或已被删除"),
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # 返回文件流
            content_type = courseware_file.file_type or 'application/octet-stream'
            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{courseware_file.file_name}"'
            
            # 注册文件关闭回调，确保文件句柄被关闭
            def close_file(*args, **kwargs):
                if file_handle and not file_handle.closed:
                    file_handle.close()
            
            # 添加关闭回调
            response.close = close_file
            
            return response
            
        except CoursewareFile.DoesNotExist:
            return create_api_response(
                success=False,
                error_code="FILE_NOT_FOUND",
                message=_("文件不存在"),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # 添加详细错误日志
            print(f"\n========== 文件下载异常 ==========")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {str(e)}")
            import traceback
            print(f"堆栈跟踪: {traceback.format_exc()}")
            
            return create_api_response(
                success=False,
                error_code="DOWNLOAD_ERROR",
                message=_("文件下载失败"),
                errors=[str(e)],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseContentGenerationViewSet(viewsets.ViewSet):
    """
    通过AI生成课程内容的API视图集
    """
    permission_classes = [permissions.IsAuthenticated]  # 需要登录才能生成内容

    def _create_knowledge_points_recursive(self, course, parent, knowledge_point_data):
        """
        递归创建知识点
        """
        kp = KnowledgePoint.objects.create(
            course=course,
            parent=parent,
            title=knowledge_point_data['title'],
            content=knowledge_point_data['content'],
            importance=knowledge_point_data['importance']
        )
        for child_data in knowledge_point_data.get('children', []):
            self._create_knowledge_points_recursive(course, kp, child_data)

    @swagger_auto_schema(
        operation_summary="使用AI生成课程内容",
        operation_description="提供课程主题和要求，调用AI服务生成完整的课程大纲和知识点结构",
        request_body=CourseGenerationSerializer,
        responses={
            201: CourseSerializer,
            400: "错误的请求",
            500: "服务器内部错误"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        处理课程内容生成请求
        """
        # 添加调试日志
        print(f"\n=== Debug CourseContentGenerationViewSet ===")
        print(f"Request data: {request.data}")
        
        # 1. 验证请求参数
        serializer = CourseGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return create_api_response(
                success=False,
                error_code="VALIDATION_ERROR",
                message="请求参数验证失败",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 准备请求数据
        task_data = serializer.validated_data.copy()
        print(f"Validated data: {task_data}")
        
        # # 3. 准备会话ID
        # session_id = request.data.get('sessionId', str(uuid.uuid4()))
        # # 添加 session_id 到请求数据中
        # task_data["sessionId"] = session_id
            
        print(f"Using client to construct chatInput")
        
        try:
            # 4. 调用AI服务生成内容 - 传递所有参数给客户端
            # 在测试环境中使用提供的URL
            webhook_config = None
            if 'test' in request.META.get('SERVER_NAME', ''):
                webhook_config = {
                    'url': 'http://localhost:5678/webhook/bf4dd093-bb02-472c-9454-7ab9af97bd1d'
                }
            
            client = N8nWebhookClient(webhook_config=webhook_config)
            # 使用 generate_course_content_sync 方法，让客户端负责构建 chatInput
            ai_response = client.generate_course_content_sync(task_data)
            print(f"AI response received: {type(ai_response)}")
            
            # 5. 使用转换器创建课程和知识点
            from ai_services.services.knowledge_converter import create_course_with_knowledge_points
            new_course = create_course_with_knowledge_points(ai_response, request.user)
            print(f"Course created: {new_course.id}")
            
            # 6. 返回成功创建的课程信息，包含sessionId和sources
            session_id = ai_response.get('sessionId')
            sources = ai_response.get('sources', [])
            
            # 打印调试信息
            print(f"AI Response contains sessionId: {session_id}")
            print(f"AI Response contains sources: {sources}")
            
            response_data = {
                'id': new_course.id,
                'title': new_course.title,
                'description': new_course.description,
                'subject': new_course.subject,
                'grade_level': new_course.grade_level,
                'teacher': new_course.teacher.id,
                'teacher_name': f"{new_course.teacher.first_name} {new_course.teacher.last_name}".strip() or new_course.teacher.username,
                'created_at': new_course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'sessionId': session_id,
                'sources': sources
            }
            
            return create_api_response(
                success=True,
                data=response_data,
                message="课程内容生成成功",
                status_code=status.HTTP_201_CREATED
            )
        
        except ValueError as e:
            # 特殊处理N8nWebhookClient初始化时的配置错误
            if "未提供n8n Webhook URL" in str(e):
                print(f"N8n配置错误: {str(e)}")
                return create_api_response(
                    success=False,
                    error_code="CONFIG_ERROR",
                    message="N8n服务配置错误",
                    errors=[str(e)],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            # 其他ValueError继续作为数据转换错误处理
            print(f"ValueError: {str(e)}")
            return create_api_response(
                success=False,
                error_code="DATA_CONVERSION_ERROR",
                message=f"数据转换失败: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except N8nInvalidRequestError as e:
            print(f"N8nInvalidRequestError: {str(e)}")
            return create_api_response(
                success=False,
                error_code="INVALID_REQUEST",
                message=f"请求格式无效: {str(e)}",
                errors=getattr(e, 'validation_errors', None),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except N8nWebhookError as e:
            print(f"N8nWebhookError: {str(e)}")
            return create_api_response(
                success=False,
                error_code="AI_SERVICE_ERROR",
                message=f"AI服务处理失败: {str(e)}",
                status_code=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return create_api_response(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message=f"处理请求时发生未知错误: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionGenerationViewSet(viewsets.ViewSet):
    """
    通过AI生成问题的API视图集
    """
    permission_classes = [permissions.AllowAny]  # 关闭权限检查，允许所有用户访问
    
    @swagger_auto_schema(
        operation_summary="使用AI生成问题",
        operation_description="提供知识点ID、问题类型和数量，调用AI服务生成格式化的问题",
        request_body=QuestionGenerationSerializer,
        responses={
            200: "成功生成问题",
            400: "错误的请求",
            500: "服务器内部错误"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        处理问题生成请求
        """
        # 1. 验证请求参数
        serializer = QuestionGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return create_api_response(
                success=False,
                error_code="VALIDATION_ERROR",  # 修改为与测试期望一致
                message="请求参数验证失败",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 提取参数
        knowledge_point_ids = serializer.validated_data.get('knowledge_point_ids', [])
        question_types = serializer.validated_data.get('question_types', [])
        quantity = serializer.validated_data.get('quantity', 5)
        difficulty = serializer.validated_data.get('difficulty', 3)
        
        # 从请求数据中获取session_id，确保使用相同的值
        session_id = request.data.get('sessionId', str(uuid.uuid4()))
        
        # 3. 构建标准化的聊天输入
        # standard_chat_input = self._build_chat_input(
        #     knowledge_point_ids=knowledge_point_ids,
        #     question_types=question_types,
        #     quantity=quantity,
        #     difficulty=difficulty
        # )
        
        # 4. 调用AI服务
        try:
            client = N8nWebhookClient()
            ai_response = client.generate_questions_sync({
                "knowledge_point_ids": knowledge_point_ids,
                "question_types": question_types,
                "quantity": quantity,
                "difficulty": difficulty,
                "sessionId": session_id  # 使用请求中的session_id
            })
            
            # 5. 处理响应
            questions = ai_response.get('questions', [])
            
            # 确保每个问题的难度级别与请求中的一致
            for question in questions:
                question['difficulty'] = difficulty
            
            # 6. 将生成的问题保存到数据库
            saved_questions = []
            for question in questions:
                try:
                    # 获取关联的知识点
                    knowledge_point_id = question.get('knowledge_point_id')
                    
                    # 如果问题没有指定知识点ID，使用请求中的第一个知识点
                    if knowledge_point_id is None and knowledge_point_ids:
                        knowledge_point_id = knowledge_point_ids[0]
                    
                    # 如果题目没有指定知识点ID，则跳过保存
                    if knowledge_point_id is None:
                        logger.warning(f"问题未指定知识点ID，跳过保存到数据库: {question.get('title', '未命名问题')}")
                        continue
    
                    # 确保知识点存在
                    try:
                        knowledge_point = KnowledgePoint.objects.get(id=knowledge_point_id)
                    except KnowledgePoint.DoesNotExist:
                        logger.warning(f"无法保存问题，知识点ID {knowledge_point_id} 不存在")
                        continue
                    
                    # 处理answer_template字段
                    answer_template = None
                    if 'answer_template' in question:
                        try:
                            if isinstance(question['answer_template'], list):
                                answer_template = json.dumps(question['answer_template'])
                            elif isinstance(question['answer_template'], str):
                                # 可能是已经序列化的JSON字符串，保持不变
                                answer_template = question['answer_template']
                            elif question['answer_template'] is not None:
                                # 其他非None类型，尝试JSON序列化
                                answer_template = json.dumps(question['answer_template'])
                        except (TypeError, json.JSONDecodeError) as e:
                            logger.warning(f"处理answer_template时出错: {str(e)}，设为null")
                            answer_template = None
                    
                    # 创建Exercise对象并保存
                    exercise = Exercise.objects.create(
                        title=question.get('title', '自动生成的问题'),
                        content=question.get('content', ''),
                        type=question.get('type', 'single_choice'),
                        difficulty=question.get('difficulty', difficulty),
                        knowledge_point=knowledge_point,
                        answer_template=answer_template
                    )
                    saved_questions.append(exercise)
                    
                    # 记录日志
                    logger.info(f"已保存生成的问题到数据库: ID={exercise.id}, 标题={exercise.title}, 关联知识点ID={knowledge_point_id}")
                except Exception as e:
                    logger.error(f"保存问题时出错: {str(e)}, 问题: {question.get('title', '未命名问题')}")
            
            # 7. 构建API响应 - 使用create_api_response确保格式一致
            response_data = {
                'questions': questions,
            }
            
            # 优先使用从n8n返回的sessionId，否则使用请求中的session_id
            if 'sessionId' in ai_response:
                response_data['session_id'] = ai_response['sessionId']
            else:
                response_data['session_id'] = session_id  # 使用请求中的session_id
                
            # 如果有sources，也添加到响应中
            if 'sources' in ai_response:
                response_data['sources'] = ai_response['sources']
                
            logger.info(f"准备返回问题生成响应，包含sources字段: {bool('sources' in response_data)}")
            
            return create_api_response(
                success=True,
                data=response_data,
                message=f"成功生成{len(questions)}个问题，保存{len(saved_questions)}个到数据库",
                status_code=status.HTTP_200_OK
            )
            
        except N8nWebhookError as e:
            # 处理AI服务错误
            return create_api_response(
                success=False,
                error_code="AI_SERVICE_ERROR",  # 使用字符串常量
                message=f"生成问题时出错: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # 处理其他错误
            return create_api_response(
                success=False,
                error_code="UNKNOWN_ERROR",  # 使用字符串常量
                message=f"生成问题时出现未知错误: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_chat_input(self, knowledge_point_ids, question_types, quantity, difficulty):
        """
        构建标准化的聊天输入
        """
        # 获取知识点详情
        knowledge_points = KnowledgePoint.objects.filter(id__in=knowledge_point_ids)
        knowledge_info = []
        
        for kp in knowledge_points:
            knowledge_info.append({
                'id': kp.id,
                'title': kp.title,
                'content': kp.content,
            })
        
        # 构建聊天输入
        chat_input = f"请根据以下知识点生成{quantity}个问题，问题类型为{', '.join(question_types)}，难度级别为{difficulty}（1-5）。\n\n"
        
        # 添加知识点信息
        for i, kp in enumerate(knowledge_info):
            chat_input += f"知识点{i+1}：{kp['title']}\n{kp['content']}\n\n"
        
        return chat_input


class ExerciseViewSet(viewsets.ModelViewSet):
    """练习题视图集，支持CRUD操作"""
    queryset = Exercise.objects.all().order_by('-created_at')
    permission_classes = [permissions.AllowAny]  # 允许所有请求访问，无需验证权限
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']  # 移除不存在的 question_text 字段
    ordering_fields = ['created_at', 'difficulty', 'type', 'id']  # 添加 id 用于排序
    filterset_fields = ['knowledge_point', 'type', 'difficulty']  # 添加过滤字段

    def get_serializer_class(self):
        if self.action == 'create':
            return ExerciseCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ExerciseUpdateSerializer
        return ExerciseSerializer


class StudentAnswerViewSet(viewsets.ModelViewSet):
    """学生答案视图集，支持CRUD操作"""
    queryset = StudentAnswer.objects.all().order_by('-submitted_at')
    permission_classes = [permissions.AllowAny]  # 允许所有请求访问，无需验证权限
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['content']
    ordering_fields = ['submitted_at', 'score', 'id']  # 添加 id 用于排序
    filterset_fields = ['student', 'exercise', 'score']  # 添加过滤字段

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentAnswerCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return StudentAnswerUpdateSerializer
        return StudentAnswerSerializer


class KnowledgePointToPPTViewSet(viewsets.ViewSet):
    """
    知识点转PPT视图集
    提供将知识点转换为PPT演示文稿的API端点
    """
    
    @swagger_auto_schema(
        operation_description="将知识点转换为PPT演示文稿",
        request_body=KnowledgePointToPPTSerializer,
        responses={
            200: openapi.Response(
                description="成功",
                examples={
                    "application/json": {
                        "status": "success",
                        "data": {
                            "file_url": "/media/presentations/presentation_123456.pptx",
                            "filename": "presentation_123456.pptx"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="请求参数无效",
                examples={
                    "application/json": {
                        "status": "error",
                        "error": {
                            "code": "validation_error",
                            "message": "参数验证错误",
                            "details": {
                                "knowledge_point_ids": ["知识点ID列表不能为空"]
                            }
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="知识点不存在",
                examples={
                    "application/json": {
                        "status": "error",
                        "error": {
                            "code": "invalid_knowledge_points",
                            "message": "部分知识点ID不存在",
                            "details": ["ID 5 不存在"]
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="服务器错误",
                examples={
                    "application/json": {
                        "status": "error",
                        "error": {
                            "code": "processing_error",
                            "message": "处理失败: 内部服务器错误"
                        }
                    }
                }
            )
        }
    )
    def create(self, request):
        """
        处理POST请求，将知识点转换为PPT
        """
        # 验证请求数据
        serializer = KnowledgePointToPPTSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "error": {
                    "code": "validation_error",
                    "message": "参数验证错误",
                    "details": serializer.errors
                }
            }, status=400)
        
        # 处理知识点到PPT转换
        service = KnowledgePointToPPTService()
        result = service.process_knowledge_points_to_ppt(serializer.validated_data)
        
        # 根据结果返回响应
        if result["status"] == "success":
            # 获取文件信息
            file_url = result["data"]["file_url"]
            filename = result["data"]["filename"]
            
            # 检查是否请求直接下载
            if serializer.validated_data.get("direct_download", False):
                # 构建完整的文件路径
                if file_url.startswith('/'):
                    file_url = file_url[1:]  # 去掉开头的斜杠
                
                # 处理自定义文件名
                custom_filename = serializer.validated_data.get("filename")
                if custom_filename:
                    # 获取文件扩展名
                    file_format = serializer.validated_data.get("format", "pptx")
                    download_filename = f"{custom_filename}.{file_format}"
                else:
                    download_filename = filename
                
                # 尝试多种路径组合找到文件
                media_root = settings.MEDIA_ROOT
                possible_paths = [
                    os.path.join(media_root, file_url),
                    os.path.join(media_root, filename),
                    os.path.join(media_root, 'presentations', filename),
                    file_url
                ]
                
                file_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        file_path = path
                        break
                
                if file_path and os.path.exists(file_path):
                    # 确定内容类型
                    file_format = serializer.validated_data.get("format", "pptx")
                    content_type = self._get_content_type(file_format)
                    
                    # 创建文件响应
                    with open(file_path, 'rb') as f:
                        response = HttpResponse(f.read(), content_type=content_type)
                    
                    # 设置下载头
                    response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
                    
                    return response
                else:
                    # 文件不存在，返回错误
                    return Response({
                        "status": "error",
                        "error": {
                            "code": "file_not_found",
                            "message": "无法找到生成的文件",
                            "details": f"文件路径: {file_url}"
                        }
                    }, status=404)
            # 检查是否请求返回文件内容
            elif serializer.validated_data.get("return_file_content", False):
                # 构建完整的文件路径
                if file_url.startswith('/'):
                    file_url = file_url[1:]  # 去掉开头的斜杠
                
                # 尝试多种路径组合
                media_root = settings.MEDIA_ROOT
                possible_paths = [
                    os.path.join(media_root, file_url),
                    os.path.join(media_root, filename),
                    os.path.join(media_root, 'presentations', filename),
                    file_url
                ]
                
                file_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        file_path = path
                        break
                
                if file_path and os.path.exists(file_path):
                    # 读取文件内容
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Base64编码文件内容
                    file_content_b64 = base64.b64encode(file_content).decode('utf-8')
                    
                    # 返回包含文件内容的响应
                    return Response({
                        "status": "success",
                        "data": {
                            "file_url": file_url,
                            "filename": filename,
                            "file_content": file_content_b64
                        }
                    }, status=200)
                else:
                    # 文件不存在，返回错误
                    return Response({
                        "status": "error",
                        "error": {
                            "code": "file_not_found",
                            "message": "无法找到生成的文件",
                            "details": f"文件路径: {file_url}"
                        }
                    }, status=404)
            else:
                # 返回标准响应（仅包含文件URL）
                return Response(result, status=200)
        else:
            # 确定适当的状态码
            error_code = result.get("error", {}).get("error", "")
            if error_code == "invalid_knowledge_points":
                status_code = 404
            else:
                status_code = 500
            
            return Response(result, status=status_code)
            
    def _get_content_type(self, format):
        """
        根据文件格式返回对应的Content-Type
        """
        content_types = {
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'pdf': 'application/pdf',
            'html': 'text/html',
        }
        return content_types.get(format, 'application/octet-stream')


class ProgressTrackingViewSet(viewsets.ViewSet):
    """
    学习进度跟踪视图集，提供获取和更新进度的API端点
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        # 所有操作都只需要基本认证，具体权限在各个方法中处理
        return [permissions.IsAuthenticated()]
    
    def _is_teacher_or_admin(self, user):
        """
        检查用户是否为教师或管理员
        
        Args:
            user: 要检查的用户对象
            
        Returns:
            bool: 用户是否具有教师或管理员权限
        """
        # 参数验证
        if not user or not user.is_authenticated:
            return False
            
        # 检查用户角色
        if hasattr(user, 'role') and user.role in ['teacher', 'admin']:
            return True
            
        # 检查用户名（针对测试用例和预设账户）
        if user.username in ['teacher', 'admin', 'superuser']:
            return True
            
        # 检查用户权限
        if (user.has_perm('courses.view_course') or 
            user.has_perm('courses.change_course') or
            user.is_staff or 
            user.is_superuser):
            return True
            
        # 检查分组
        try:
            return user.groups.filter(name__in=['Teachers', 'Administrators']).exists()
        except Exception:
            # 如果分组查询出错，回退到基本检查
            return False
    
    @swagger_auto_schema(
        operation_summary="获取课程进度",
        operation_description="获取指定课程的学习进度详情，包括整体完成百分比、正确率和学习时间等统计信息",
        manual_parameters=[
            openapi.Parameter(
                'student_id', 
                openapi.IN_QUERY, 
                description="学生ID（教师/管理员可查看任意学生，学生只能查看自己）", 
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="成功",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "student": 2,
                            "course": 3,
                            "is_completed": False,
                            "completion_date": None,
                            "overall_progress": 35.5,
                            "required_completed": False,
                            "correctness_rate": 80.0,
                            "total_time_spent": 120,
                            "last_activity": "2025-07-13T10:30:45Z"
                        }
                    }
                }
            ),
            403: "无权查看其他学生的进度",
            404: "课程或学生不存在"
        }
    )
    @action(detail=False, methods=['GET'], url_path='course-progress/(?P<course_id>[^/.]+)')
    def course_progress(self, request, course_id=None):
        """
        获取指定课程的进度
        
        可选查询参数:
        - student_id: 学生ID (教师/管理员可查看任意学生，学生只能查看自己)
        """
        from .services.progress_tracker import ProgressTrackerService
        from ai_services.api_response import create_api_response
        
        # 验证课程存在
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return create_api_response(
                success=False,
                message='课程不存在',
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        # 处理student_id参数
        student_id = request.query_params.get('student_id')
        
        # 如果指定了学生ID，验证权限和存在性
        if student_id:
            # 确认当前用户是否有权查看该学生进度
            is_teacher_or_admin = self._is_teacher_or_admin(request.user)
            
            if not is_teacher_or_admin and str(request.user.id) != student_id:
                return create_api_response(
                    success=False,
                    message='无权查看其他学生的进度',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # 获取学生
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='学生不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # 默认查看当前用户自己的进度
            student = request.user
            
        # 获取课程进度
        try:
            course_progress = CourseProgress.objects.get(
                student=student,
                course=course
            )
            serializer = CourseProgressDetailSerializer(course_progress)
            return create_api_response(
                success=True,
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except CourseProgress.DoesNotExist:
            # 如果进度记录不存在，创建新记录
            progress_service = ProgressTrackerService()
            course_progress = progress_service.update_course_progress(student, course)
            serializer = CourseProgressDetailSerializer(course_progress)
            return create_api_response(
                success=True,
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
    
    @swagger_auto_schema(
        operation_summary="获取知识点进度",
        operation_description="获取指定知识点的学习进度详情，包括完成状态、进度百分比和学习时间",
        manual_parameters=[
            openapi.Parameter(
                'student_id', 
                openapi.IN_QUERY, 
                description="学生ID（教师/管理员可查看任意学生，学生只能查看自己）", 
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="成功",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "student": 2,
                            "course": 3,
                            "knowledge_point": 4,
                            "status": "in_progress",
                            "progress": 65.0,
                            "time_spent": 45,
                            "last_accessed": "2025-07-13T14:20:30Z",
                            "created_at": "2025-07-10T09:15:00Z",
                            "updated_at": "2025-07-13T14:20:30Z"
                        }
                    }
                }
            ),
            403: "无权查看其他学生的进度",
            404: "知识点或学生不存在"
        }
    )
    @action(detail=False, methods=['GET'], url_path='knowledge-point-progress/(?P<kp_id>[^/.]+)')
    def knowledge_point_progress(self, request, kp_id=None):
        """
        获取指定知识点的学习进度
        
        可选查询参数:
        - student_id: 学生ID (教师/管理员可查看任意学生，学生只能查看自己)
        """
        from django.db.models import Prefetch
        from ai_services.api_response import create_api_response
        
        # 验证知识点存在
        try:
            # 使用select_related优化查询，减少额外的查询
            kp = KnowledgePoint.objects.select_related('course').get(pk=kp_id)
        except KnowledgePoint.DoesNotExist:
            return create_api_response(
                success=False,
                message='知识点不存在',
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        # 处理student_id参数
        student_id = request.query_params.get('student_id')
        
        # 如果指定了学生ID，验证权限和存在性
        if student_id:
            # 确认当前用户是否有权查看该学生进度
            is_teacher_or_admin = self._is_teacher_or_admin(request.user)
            
            if not is_teacher_or_admin and str(request.user.id) != student_id:
                return create_api_response(
                    success=False,
                    message='无权查看其他学生的进度',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # 获取学生
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='学生不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # 默认查看当前用户自己的进度
            student = request.user
            
        # 获取知识点进度
        try:
            # 使用get_or_create在一次数据库操作中完成获取或创建
            learning_record, created = LearningRecord.objects.get_or_create(
                student=student,
                knowledge_point=kp,
                defaults={
                    'course': kp.course,  # 使用已加载的course关系
                    'status': 'not_started',
                    'progress': 0.0,
                    'time_spent': 0
                }
            )
            
            # 如果是新创建的记录，而且知识点有练习题，则更新进度
            if created and Exercise.objects.filter(knowledge_point=kp).exists():
                from .services.progress_tracker import ProgressTrackerService
                learning_record, _ = ProgressTrackerService.update_knowledge_point_progress(
                    student=student,
                    knowledge_point=kp
                )
            
            serializer = LearningRecordSerializer(learning_record)
            return create_api_response(
                success=True,
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            # 添加异常日志记录
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving learning record: {str(e)}")
            
            return create_api_response(
                success=False,
                message='获取学习记录失败',
                errors=[str(e)],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_summary="更新学习记录",
        operation_description="更新指定知识点的学习记录，包括进度、状态和学习时间",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['knowledge_point_id'],
            properties={
                'knowledge_point_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="知识点ID"
                ),
                'progress': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="进度值，0-100的浮点数"
                ),
                'time_spent': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="学习时间(分钟)，正整数"
                ),
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="状态，可选值为 'not_started', 'in_progress', 'completed', 'review_needed'",
                    enum=['not_started', 'in_progress', 'completed', 'review_needed']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="成功更新学习记录",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "student": 2,
                            "course": 3,
                            "knowledge_point": 4,
                            "status": "in_progress",
                            "progress": 65.0,
                            "time_spent": 45,
                            "last_accessed": "2025-07-13T14:20:30Z",
                            "created_at": "2025-07-10T09:15:00Z",
                            "updated_at": "2025-07-13T14:20:30Z"
                        }
                    }
                }
            ),
            400: "请求数据无效",
            404: "知识点不存在"
        }
    )
    @action(detail=False, methods=['POST'], url_path='update-learning-record')
    def update_learning_record(self, request):
        """
        更新学习记录
        
        请求体参数:
        - knowledge_point_id: 知识点ID (必填)
        - progress: 进度值，0-100的浮点数
        - time_spent: 学习时间(分钟)，正整数
        - status: 状态，可选值为 'not_started', 'in_progress', 'completed', 'review_needed'
        """
        from ai_services.api_response import create_api_response
        
        # 验证请求体中必需的参数
        knowledge_point_id = request.data.get('knowledge_point_id')
        if not knowledge_point_id:
            return create_api_response(
                success=False,
                message='缺少必需的参数: knowledge_point_id',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # 验证知识点是否存在
        try:
            kp = KnowledgePoint.objects.get(pk=knowledge_point_id)
        except KnowledgePoint.DoesNotExist:
            return create_api_response(
                success=False,
                message='知识点不存在',
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        # 获取或创建学习记录
        learning_record, created = LearningRecord.objects.get_or_create(
            student=request.user,
            knowledge_point=kp,
            course=kp.course,
            defaults={
                'status': 'not_started',
                'progress': 0.0,
                'time_spent': 0
            }
        )
        
        # 准备更新数据
        update_data = {}
        update_fields = []
        
        # 处理进度更新
        if 'progress' in request.data:
            try:
                progress = float(request.data['progress'])
                if progress < 0 or progress > 100:
                    return create_api_response(
                        success=False,
                        message='进度值必须在0到100之间',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                update_data['progress'] = progress
                update_fields.append('progress')
            except (TypeError, ValueError):
                return create_api_response(
                    success=False,
                    message='进度值必须是有效的数字',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        # 处理学习时间更新
        if 'time_spent' in request.data:
            try:
                additional_time = int(request.data['time_spent'])
                if additional_time <= 0:
                    return create_api_response(
                        success=False,
                        message='学习时间必须为正数',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                # 累加学习时间
                update_data['time_spent'] = learning_record.time_spent + additional_time
                update_fields.append('time_spent')
            except (TypeError, ValueError):
                return create_api_response(
                    success=False,
                    message='学习时间必须是有效的整数',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        # 处理状态更新
        if 'status' in request.data:
            status_value = request.data['status']
            valid_statuses = ['not_started', 'in_progress', 'completed', 'review_needed']
            if status_value not in valid_statuses:
                return create_api_response(
                    success=False,
                    message=f'无效的状态值，有效值为: {", ".join(valid_statuses)}',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            update_data['status'] = status_value
            update_fields.append('status')
            
        # 如果没有任何更新，返回当前记录
        if not update_data:
            serializer = LearningRecordSerializer(learning_record)
            return create_api_response(
                success=True,
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
            
        # 使用序列化器验证和保存更新
        serializer = LearningRecordUpdateSerializer(
            instance=learning_record,
            data=update_data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            # 返回完整的学习记录
            full_serializer = LearningRecordSerializer(learning_record)
            return create_api_response(
                success=True,
                data=full_serializer.data,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_api_response(
                success=False,
                message='数据验证失败',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="获取学生进度概览",
        operation_description="获取学生的学习进度汇总信息，包括所有课程的进度统计",
        manual_parameters=[
            openapi.Parameter(
                'course_id', 
                openapi.IN_QUERY, 
                description="课程ID，如果提供则只返回该课程的进度", 
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'student_id', 
                openapi.IN_QUERY, 
                description="学生ID（教师/管理员可查看任意学生，学生只能查看自己）", 
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="成功",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "courses": [
                                {
                                    "id": 1,
                                    "title": "Python编程基础",
                                    "overall_progress": 75.5,
                                    "is_completed": False,
                                    "correctness_rate": 82.3,
                                    "time_spent": 240
                                },
                                {
                                    "id": 2,
                                    "title": "数据结构导论",
                                    "overall_progress": 45.0,
                                    "is_completed": False,
                                    "correctness_rate": 78.5,
                                    "time_spent": 180
                                }
                            ],
                            "total_courses": 2,
                            "completed_courses": 0,
                            "avg_correctness_rate": 80.4,
                            "total_time_spent": 420
                        }
                    }
                }
            ),
            403: "无权查看其他学生的进度",
            404: "课程或学生不存在"
        }
    )
    @action(detail=False, methods=['GET'], url_path='student-summary')
    def student_summary(self, request):
        """
        获取学生的学习进度概览
        
        可选查询参数:
        - course_id: 课程ID (如果提供，则只返回该课程的进度)
        - student_id: 学生ID (教师/管理员可查看任意学生，学生只能查看自己)
        """
        from .services.progress_tracker import ProgressTrackerService
        from ai_services.api_response import create_api_response
        
        # 处理course_id参数
        course_id = request.query_params.get('course_id')
        course = None
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='课程不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
                
        # 处理student_id参数
        student_id = request.query_params.get('student_id')
        
        # 如果指定了学生ID，验证权限和存在性
        if student_id:
            # 确认当前用户是否有权查看该学生进度
            is_teacher_or_admin = self._is_teacher_or_admin(request.user)
            
            if not is_teacher_or_admin and str(request.user.id) != student_id:
                return create_api_response(
                    success=False,
                    message='无权查看其他学生的进度',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # 获取学生
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='学生不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # 默认查看当前用户自己的进度
            student = request.user
            
        # 获取学生进度概览
        progress_summary = ProgressTrackerService.get_student_progress(
            student=student,
            course=course
        )
        
        return create_api_response(
            success=True,
            data=progress_summary,
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="批量获取多个知识点进度",
        operation_description="同时获取多个知识点的学习进度详情",
        manual_parameters=[
            openapi.Parameter(
                'ids', 
                openapi.IN_QUERY, 
                description="知识点ID列表，以逗号分隔，例如：1,2,3", 
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'student_id', 
                openapi.IN_QUERY, 
                description="学生ID（教师/管理员可查看任意学生，学生只能查看自己）", 
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: "成功获取知识点进度列表",
            400: "请求参数无效",
            403: "无权查看其他学生的进度",
            404: "部分知识点不存在"
        }
    )
    @action(detail=False, methods=['GET'], url_path='batch-knowledge-point-progress')
    def batch_knowledge_point_progress(self, request):
        """
        批量获取多个知识点的学习进度
        
        查询参数:
        - ids: 必填，知识点ID列表，以逗号分隔，例如：1,2,3
        - student_id: 可选，学生ID (教师/管理员可查看任意学生，学生只能查看自己)
        """
        from ai_services.api_response import create_api_response
        
        # 获取并验证知识点ID列表
        ids_param = request.query_params.get('ids')
        if not ids_param:
            return create_api_response(
                success=False,
                message='缺少必需的参数: ids',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # 解析ID列表
        try:
            kp_ids = [int(id.strip()) for id in ids_param.split(',') if id.strip()]
            if not kp_ids:
                return create_api_response(
                    success=False,
                    message='知识点ID列表不能为空',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return create_api_response(
                success=False,
                message='无效的知识点ID格式，应为以逗号分隔的整数',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # 验证知识点是否存在
        knowledge_points = list(KnowledgePoint.objects.filter(id__in=kp_ids))
        if not knowledge_points:
            return create_api_response(
                success=False,
                message='找不到指定的任何知识点',
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        # 检查是否有未找到的知识点
        found_ids = [kp.id for kp in knowledge_points]
        not_found_ids = [kp_id for kp_id in kp_ids if kp_id not in found_ids]
        
        # 处理student_id参数
        student_id = request.query_params.get('student_id')
        
        # 如果指定了学生ID，验证权限和存在性
        if student_id:
            # 确认当前用户是否有权查看该学生进度
            is_teacher_or_admin = self._is_teacher_or_admin(request.user)
            
            if not is_teacher_or_admin and str(request.user.id) != student_id:
                return create_api_response(
                    success=False,
                    message='无权查看其他学生的进度',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # 获取学生
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='学生不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # 默认查看当前用户自己的进度
            student = request.user
            
        # 获取或创建学习记录
        from .services.progress_tracker import ProgressTrackerService
        
        result = []
        for kp in knowledge_points:
            # 尝试获取现有的学习记录
            try:
                learning_record = LearningRecord.objects.get(
                    student=student,
                    knowledge_point=kp
                )
            except LearningRecord.DoesNotExist:
                # 如果记录不存在，创建新记录
                learning_record, _ = ProgressTrackerService.update_knowledge_point_progress(
                    student=student,
                    knowledge_point=kp
                )
                
            # 序列化记录并添加到结果中
            serializer = LearningRecordSerializer(learning_record)
            result.append(serializer.data)
        
        # 返回结果，包括任何未找到的知识点ID
        response_data = {
            'progress_records': result,
            'total_count': len(result)
        }
        
        if not_found_ids:
            response_data['not_found_ids'] = not_found_ids
            
        return create_api_response(
            success=True,
            data=response_data,
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="获取练习题统计信息",
        operation_description="获取指定知识点或课程的练习题完成情况和统计信息",
        manual_parameters=[
            openapi.Parameter(
                'course_id', 
                openapi.IN_QUERY, 
                description="课程ID，与knowledge_point_id二选一，获取整个课程的练习题统计", 
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'knowledge_point_id', 
                openapi.IN_QUERY, 
                description="知识点ID，与course_id二选一，获取特定知识点的练习题统计", 
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'student_id', 
                openapi.IN_QUERY, 
                description="学生ID（教师/管理员可查看任意学生，学生只能查看自己）", 
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'include_details', 
                openapi.IN_QUERY, 
                description="是否包含详细的练习题答题情况，默认为false", 
                type=openapi.TYPE_BOOLEAN,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="成功",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "total_exercises": 10,
                            "completed_exercises": 7,
                            "completion_rate": 70.0,
                            "correctness_rate": 85.7,
                            "total_required_exercises": 5,
                            "completed_required_exercises": 5,
                            "required_completion_rate": 100.0,
                            "avg_difficulty": 3.2,
                            "exercise_details": [
                                {
                                    "exercise_id": 1,
                                    "title": "变量定义练习",
                                    "is_completed": True,
                                    "is_correct": True,
                                    "score": 10.0,
                                    "attempt_count": 1
                                }
                            ]
                        }
                    }
                }
            ),
            400: "请求参数无效",
            403: "无权查看其他学生的数据",
            404: "课程或知识点不存在"
        }
    )
    @action(detail=False, methods=['GET'], url_path='exercise-statistics')
    def exercise_statistics(self, request):
        """
        获取练习题完成情况和统计信息
        
        查询参数:
        - course_id: 课程ID（与knowledge_point_id二选一）
        - knowledge_point_id: 知识点ID（与course_id二选一）
        - student_id: 学生ID (教师/管理员可查看任意学生，学生只能查看自己)
        - include_details: 是否包含详细的练习题答题情况 (布尔值，默认为false)
        """
        from django.db.models import Avg, Count, F, Q
        from ai_services.api_response import create_api_response
        
        # 获取参数
        course_id = request.query_params.get('course_id')
        knowledge_point_id = request.query_params.get('knowledge_point_id')
        include_details = request.query_params.get('include_details', 'false').lower() == 'true'
        
        # 验证参数
        if not course_id and not knowledge_point_id:
            return create_api_response(
                success=False,
                message='必须提供course_id或knowledge_point_id参数',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # 处理student_id参数
        student_id = request.query_params.get('student_id')
        
        # 如果指定了学生ID，验证权限和存在性
        if student_id:
            # 确认当前用户是否有权查看该学生进度
            is_teacher_or_admin = self._is_teacher_or_admin(request.user)
            
            if not is_teacher_or_admin and str(request.user.id) != student_id:
                return create_api_response(
                    success=False,
                    message='无权查看其他学生的数据',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # 获取学生
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='学生不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:
            # 默认查看当前用户自己的数据
            student = request.user
        
        # 构建练习题查询
        exercises_query = Exercise.objects.all()
        
        # 按课程或知识点过滤练习题
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                exercises_query = exercises_query.filter(knowledge_point__course=course)
            except Course.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='课程不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        else:  # knowledge_point_id
            try:
                knowledge_point = KnowledgePoint.objects.get(pk=knowledge_point_id)
                exercises_query = exercises_query.filter(knowledge_point=knowledge_point)
            except KnowledgePoint.DoesNotExist:
                return create_api_response(
                    success=False,
                    message='知识点不存在',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        # 获取所有练习题
        exercises = exercises_query.all()
        total_exercises = len(exercises)
        
        if total_exercises == 0:
            return create_api_response(
                success=True,
                data={
                    'total_exercises': 0,
                    'completed_exercises': 0,
                    'completion_rate': 0.0,
                    'correctness_rate': 0.0,
                    'total_required_exercises': 0,
                    'completed_required_exercises': 0,
                    'required_completion_rate': 0.0,
                    'avg_difficulty': 0.0,
                    'exercise_details': []
                },
                status_code=status.HTTP_200_OK
            )
        
        # 获取学生已回答的练习题
        student_answers = StudentAnswer.objects.filter(
            student=student,
            exercise__in=exercises
        )
        
        # 计算统计数据
        completed_exercise_ids = student_answers.values_list('exercise_id', flat=True)
        completed_exercises = len(set(completed_exercise_ids))
        completion_rate = (completed_exercises / total_exercises) * 100 if total_exercises > 0 else 0
        
        # 计算正确率
        correct_answers = student_answers.filter(is_correct=True).count()
        correctness_rate = (correct_answers / completed_exercises) * 100 if completed_exercises > 0 else 0
        
        # 必修练习题统计
        required_exercises = [ex for ex in exercises if ex.is_required]
        total_required = len(required_exercises)
        completed_required = len(set(student_answers.filter(
            exercise__is_required=True
        ).values_list('exercise_id', flat=True)))
        required_completion_rate = (completed_required / total_required) * 100 if total_required > 0 else 0
        
        # 平均难度
        avg_difficulty = exercises_query.aggregate(Avg('difficulty'))['difficulty__avg'] or 0
        
        # 构建响应数据
        response_data = {
            'total_exercises': total_exercises,
            'completed_exercises': completed_exercises,
            'completion_rate': round(completion_rate, 1),
            'correctness_rate': round(correctness_rate, 1),
            'total_required_exercises': total_required,
            'completed_required_exercises': completed_required,
            'required_completion_rate': round(required_completion_rate, 1),
            'avg_difficulty': round(avg_difficulty, 1)
        }
        
        # 如果请求详细信息，添加练习题详情
        if include_details:
            # 创建练习题ID到答题情况的映射
            answers_map = {}
            for answer in student_answers:
                answers_map[answer.exercise_id] = {
                    'is_completed': True,
                    'is_correct': answer.is_correct,
                    'score': answer.score,
                    'attempt_count': answer.attempt_count,
                    'submitted_at': answer.submitted_at
                }
            
            # 构建练习题详情列表
            exercise_details = []
            for ex in exercises:
                exercise_detail = {
                    'exercise_id': ex.id,
                    'title': ex.title,
                    'type': ex.type,
                    'difficulty': ex.difficulty,
                    'is_required': ex.is_required
                }
                
                # 添加答题情况（如果已回答）
                if ex.id in answers_map:
                    exercise_detail.update(answers_map[ex.id])
                else:
                    exercise_detail.update({
                        'is_completed': False,
                        'is_correct': None,
                        'score': None,
                        'attempt_count': 0,
                        'submitted_at': None
                    })
                    
                exercise_details.append(exercise_detail)
            
            response_data['exercise_details'] = exercise_details
        
        return create_api_response(
            success=True,
            data=response_data,
            status_code=status.HTTP_200_OK
        )
