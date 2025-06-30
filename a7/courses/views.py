from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Course, KnowledgePoint, Courseware
from .serializers import (
    CourseSerializer, 
    CourseCreateSerializer, 
    CourseUpdateSerializer,
    KnowledgePointSerializer,
    KnowledgePointCreateSerializer,
    KnowledgePointUpdateSerializer,
    CoursewareSerializer,
    CoursewareCreateSerializer,
    CoursewareUpdateSerializer
)
from .permissions import (
    IsTeacherOrAdmin, 
    IsCourseTeacherOrAdmin, 
    IsKnowledgePointCourseTeacherOrAdmin,
    IsCoursewareCreatorOrAdmin
)
from .utils import validate_required_params

# AI服务集成
from ai_services.services.n8n_webhook.client import N8nWebhookClient
from ai_services.services.n8n_webhook.exceptions import N8nWebhookError, N8nInvalidRequestError
from ai_services.api_response import create_api_response
from django.db import transaction
from rest_framework.views import APIView


class CourseViewSet(viewsets.ModelViewSet):
    """
    课程视图集，提供课程的增删改查功能
    """
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
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
        if self.action == 'create':
            # 只有教师和管理员可以创建课程
            self.permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 只有课程创建者和管理员可以修改或删除课程
            self.permission_classes = [permissions.IsAuthenticated, IsCourseTeacherOrAdmin]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="获取当前用户创建的课程列表",
        operation_description="返回当前已认证用户创建的所有课程"
    )
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """
        获取当前用户创建的课程列表
        """
        try:
            user = request.user
            queryset = self.queryset.filter(teacher=user)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
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
    permission_classes = [permissions.IsAuthenticated]
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
            # 只有教师和管理员可以创建知识点
            self.permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 只有知识点所属课程的创建者和管理员可以修改或删除知识点
            self.permission_classes = [permissions.IsAuthenticated, IsKnowledgePointCourseTeacherOrAdmin]
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
    serializer_class = CoursewareSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'type']
    ordering_fields = ['created_at', 'title', 'type']
    
    def get_queryset(self):
        """
        可根据URL参数过滤课件：
        - course: 按课程ID过滤
        - type: 按课件类型过滤
        """
        queryset = super().get_queryset()
        
        # 按课程过滤
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # 按类型过滤
        courseware_type = self.request.query_params.get('type')
        if courseware_type:
            queryset = queryset.filter(type=courseware_type)
            
        return queryset
    
    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        """
        if self.action == 'create':
            return CoursewareCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CoursewareUpdateSerializer
        return CoursewareSerializer
    
    def get_permissions(self):
        """
        根据操作类型设置不同的权限
        """
        if self.action == 'create':
            # 只有教师和管理员可以创建课件
            self.permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 只有课件创建者和管理员可以修改或删除课件
            self.permission_classes = [permissions.IsAuthenticated, IsCoursewareCreatorOrAdmin]
        return super().get_permissions()
    
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
        validation_error = validate_required_params(request, ['course'])
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


class CourseContentGenerationView(APIView):
    """
    通过AI生成课程内容的API视图
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

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
        request_body=CourseCreateSerializer, # 这里可以后面定义一个更精确的序列化器
        responses={
            201: CourseSerializer,
            400: "错误的请求",
            500: "服务器内部错误"
        }
    )
    def post(self, request, *args, **kwargs):
        """
        处理课程内容生成请求
        """
        # 1. 验证请求参数
        required_params = ['course_name', 'chapter_count', 'course_description', 'subject', 'grade_level']
        missing_params = [param for param in required_params if param not in request.data]
        if missing_params:
            return create_api_response(
                success=False,
                error_code="MISSING_PARAMETERS",
                message=f"缺少必要参数: {', '.join(missing_params)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        task_data = {
            "course_name": request.data.get('course_name'),
            "chapter_count": request.data.get('chapter_count'),
            "course_description": request.data.get('course_description'),
            "subject": request.data.get('subject'),
            "grade_level": request.data.get('grade_level'),
            "additional_requirements": request.data.get('additional_requirements', '')
        }

        try:
            # 2. 调用AI服务生成内容
            client = N8nWebhookClient()
            ai_response = client.process_ai_task_sync('courseGeneration', task_data)

            # 3. 在数据库事务中创建课程和知识点
            with transaction.atomic():
                # 创建课程
                course_info = ai_response['course']
                new_course = Course.objects.create(
                    title=course_info['title'],
                    description=course_info['description'],
                    subject=course_info['subject'],
                    grade_level=course_info['grade_level'],
                    teacher=request.user
                )

                # 递归创建知识点
                for kp_data in ai_response['knowledge_points']:
                    self._create_knowledge_points_recursive(new_course, None, kp_data)
            
            # 4. 返回成功创建的课程信息
            serializer = CourseSerializer(new_course)
            return create_api_response(
                success=True,
                data=serializer.data,
                message="课程内容生成成功",
                status_code=status.HTTP_201_CREATED
            )

        except (N8nWebhookError, N8nInvalidRequestError) as e:
            return create_api_response(
                success=False,
                error_code="AI_SERVICE_ERROR",
                message=f"AI服务处理失败: {str(e)}",
                status_code=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        except Exception as e:
            return create_api_response(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message=f"处理请求时发生未知错误: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
