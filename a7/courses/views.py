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
    CoursewareUpdateSerializer,
    CourseGenerationSerializer
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


class CourseContentGenerationViewSet(viewsets.ViewSet):
    """
    通过AI生成课程内容的API视图集
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
        
        # 3. 自动构建标准格式的chatInput，确保提示的正确性
        # 无论用户是否提供了chatInput，都使用系统构建的标准格式
        course_name = task_data.get('course_name')
        chapter_count = task_data.get('chapter_count')
        course_description = task_data.get('course_description')
        subject = task_data.get('subject')
        grade_level = task_data.get('grade_level')
        additional_requirements = task_data.get('additional_requirements', '')
        
        # 构建标准格式的chatInput
        standard_chat_input = f"""
请根据以下信息生成一门课程的知识点结构，并以严格的JSON格式返回结果。

输入信息：
- 课程名称：{course_name}
- 章节数量：{chapter_count}
- 课程描述：{course_description}
- 学科：{subject}
- 年级水平：{grade_level}
- 额外要求：{additional_requirements}

你必须严格按照以下JSON格式返回结果，不要添加任何额外文本、说明或Markdown标记：

```json
{{
  "course": {{
    "title": "课程标题",
    "description": "课程描述",
    "subject": "学科名称",
    "grade_level": "年级水平"
  }},
  "knowledge_points": [
    {{
      "title": "顶级知识点1标题",
      "content": "详细内容描述",
      "importance": 数字(1-10),
      "children": [
        {{
          "title": "子知识点1.1标题",
          "content": "详细内容描述",
          "importance": 数字(1-10),
          "children": []
        }},
        {{
          "title": "子知识点1.2标题",
          "content": "详细内容描述",
          "importance": 数字(1-10),
          "children": []
        }}
      ]
    }},
    {{
      "title": "顶级知识点2标题",
      "content": "详细内容描述",
      "importance": 数字(1-10),
      "children": []
    }}
  ]
}}
```

请注意：
1. 顶级知识点数量应与章节数量相匹配（{chapter_count}个）
2. 每个知识点必须包含title、content和importance字段
3. importance必须是1到10之间的整数
4. children是一个数组，可以为空，也可以包含子知识点
5. 子知识点必须遵循相同的结构（title, content, importance, children）
6. 不要在JSON外添加任何解释或说明文字
7. 确保你的JSON格式正确且有效，系统将直接解析此JSON

此课程内容将直接用于教育系统，格式错误将导致系统无法处理。
        """
        
        # 用系统构建的标准格式替换用户提供的chatInput
        task_data['chatInput'] = standard_chat_input
        
        # 如果用户没有提供sessionId，生成一个
        if 'sessionId' not in task_data:
            import uuid
            task_data['sessionId'] = str(uuid.uuid4())
            
        print(f"Using standardized chatInput format")
        
        try:
            # 4. 调用AI服务生成内容 - 使用通用的process_ai_task_sync方法
            # 在测试环境中使用提供的URL
            webhook_config = None
            if 'test' in request.META.get('SERVER_NAME', ''):
                webhook_config = {
                    'url': 'http://localhost:5678/webhook/bf4dd093-bb02-472c-9454-7ab9af97bd1d'
                }
            
            client = N8nWebhookClient(webhook_config=webhook_config)
            ai_response = client.process_ai_task_sync('courseGeneration', task_data)
            print(f"AI response received: {type(ai_response)}")
            
            # 5. 使用转换器创建课程和知识点
            from ai_services.services.knowledge_converter import create_course_with_knowledge_points
            new_course = create_course_with_knowledge_points(ai_response, request.user)
            print(f"Course created: {new_course.id}")
            
            # 6. 返回成功创建的课程信息
            course_serializer = CourseSerializer(new_course)
            return create_api_response(
                success=True,
                data=course_serializer.data,
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
