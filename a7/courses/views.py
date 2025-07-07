from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course, KnowledgePoint, Courseware, Exercise, StudentAnswer
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
    CourseGenerationSerializer,
    QuestionGenerationSerializer,
    ExerciseSerializer,
    ExerciseCreateSerializer,
    ExerciseUpdateSerializer,
    StudentAnswerSerializer,
    StudentAnswerCreateSerializer,
    StudentAnswerUpdateSerializer
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
import json
import uuid
from datetime import datetime
from drf_yasg import openapi


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
            201: "成功生成问题",
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
                error_code="VALIDATION_ERROR",
                message="请求参数验证失败",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 准备请求数据
        task_data = serializer.validated_data.copy()
        
        # 3. 自动构建标准格式的chatInput，确保提示的正确性
        knowledge_point_ids = task_data.get('knowledge_point_ids')
        question_types = task_data.get('question_types')
        quantity = task_data.get('quantity')
        difficulty = task_data.get('difficulty')
        
        # 获取知识点详情，用于提示
        knowledge_points = []
        for kp_id in knowledge_point_ids:
            try:
                kp = KnowledgePoint.objects.get(id=kp_id)
                knowledge_points.append({
                    'id': kp.id,
                    'title': kp.title,
                    'content': kp.content
                })
            except KnowledgePoint.DoesNotExist:
                return create_api_response(
                    success=False,
                    error_code="NOT_FOUND",
                    message=f"知识点ID为{kp_id}的知识点不存在",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        # 根据题型构建格式指南部分
        format_guidelines = ""

        if 'single_choice' in question_types:
            format_guidelines += """
单选题格式示例：
{
  "title": "简短问题标题",
  "content": "完整的问题描述，包含必要背景",
  "type": "single_choice",
  "difficulty": 3,
  "answer_template": ["正确选项", "干扰选项1", "干扰选项2", "干扰选项3"],
  "knowledge_point_id": 相关知识点ID
}

选项应该足够干扰性但又合理，至少包含2个选项。
"""

        if 'multiple_choice' in question_types:
            format_guidelines += """
多选题格式示例：
{
  "title": "简短问题标题",
  "content": "完整的问题描述，包含必要背景",
  "type": "multiple_choice",
  "difficulty": 3,
  "answer_template": ["正确选项1", "正确选项2", "干扰选项1", "干扰选项2"],
  "knowledge_point_id": 相关知识点ID
}

选项应该足够干扰性但又合理，至少包含3个选项。
"""

        if 'fill_blank' in question_types:
            format_guidelines += """
填空题格式示例：
{
  "title": "简短问题标题",
  "content": "句子中包含___或[BLANK]作为填空位置，用于学生填写答案。",
  "type": "fill_blank",
  "difficulty": 3,
  "answer_template": ["正确答案1", "其他可接受答案"],
  "knowledge_point_id": 相关知识点ID
}

填空题必须在content中使用___或[BLANK]标记填空位置。
"""

        if 'short_answer' in question_types:
            format_guidelines += """
简答题格式示例：
{
  "title": "简短问题标题",
  "content": "需要学生以简短段落回答的问题",
  "type": "short_answer",
  "difficulty": 3,
  "answer_template": "参考答案或评分要点描述",
  "knowledge_point_id": 相关知识点ID
}
"""

        if 'coding' in question_types:
            format_guidelines += """
编程题格式示例：
{
  "title": "简短问题标题",
  "content": "详细的编程要求，包括输入输出格式、约束条件等",
  "type": "coding",
  "difficulty": 3,
  "answer_template": "示例代码解答或解题思路",
  "knowledge_point_id": 相关知识点ID
}
"""

        # 将格式指南添加到chatInput中
        standard_chat_input = f"""
请根据以下知识点信息生成教学练习题，并以严格的JSON格式返回结果。

知识点信息：
{json.dumps(knowledge_points, ensure_ascii=False, indent=2)}

要求：
- 生成{quantity}道练习题
- 题目类型：{', '.join(question_types)}
- 难度等级：{difficulty if difficulty else '1-5之间'}

格式要求：
{format_guidelines}

重要提示：
1. 每个问题必须关联到提供的知识点ID之一
2. 必须严格遵循上面提供的题型格式规范
3. 请确保你的响应是一个有效的JSON，带有questions数组
4. 不要在JSON外添加任何解释或说明文字

你必须严格按照以下JSON格式返回结果，不要添加任何额外文本、说明或Markdown标记：

```json
{{
  "questions": [
    // 第一个问题...符合上述格式要求
    // 第二个问题...符合上述格式要求
    // 更多问题...
  ]
}}
```
        """
        
        # 用系统构建的标准格式替换用户提供的chatInput
        task_data['chatInput'] = standard_chat_input
        
        # 如果用户没有提供sessionId，生成一个
        if 'sessionId' not in task_data:
            task_data['sessionId'] = str(uuid.uuid4())
        
        try:
            # 4. 调用AI服务生成问题
            client = N8nWebhookClient()
            ai_response = client.generate_questions_sync(task_data)
            
            # 5. 处理生成的问题
            questions = ai_response.get('questions', [])
            
            # 6. 验证生成的问题格式
            if not questions:
                return create_api_response(
                    success=False,
                    error_code="EMPTY_RESPONSE",
                    message="AI未能生成任何问题",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # 7. 将生成的问题存储在会话中，以便后续导出
            # 创建唯一的会话键
            session_key = f"generated_questions_{uuid.uuid4()}"
            
            # 将问题和创建时间存储在会话中
            request.session[session_key] = {
                'questions': questions,
                'created_at': datetime.now().isoformat(),
                'knowledge_point_ids': knowledge_point_ids,
                'question_types': question_types
            }
            
            # 8. 将生成的问题保存到数据库
            save_result = self.save_to_database(questions, request.user if request.user.is_authenticated else None)
            
            # 在响应中包含会话键和已保存的题目ID，以便前端可以用它来请求导出
            return create_api_response(
                success=True,
                message="问题生成成功并已保存到数据库",
                data={
                    'questions': questions,
                    'session_key': session_key,  # 添加会话键到响应中
                    'saved_exercises': save_result['saved_ids'],  # 添加已保存的题目ID
                    'failed_exercises': save_result['failed_count']  # 添加保存失败的题目数量
                },
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"生成问题时出错: {str(e)}")
            
            # 格式化错误响应
            error_message = str(e)
            if hasattr(e, 'message'):
                error_message = e.message
                
            return create_api_response(
                success=False,
                error_code="GENERATION_ERROR",
                message=f"生成问题时出错: {error_message}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def save_to_database(self, questions, user=None):
        """
        将生成的问题保存到数据库中
        
        参数:
        - questions: 问题列表，包含题目详情
        - user: 创建用户（可选），当前Exercise模型不支持记录创建者，暂不使用
        
        返回:
        - dict: 包含保存成功的题目ID列表和失败数量
        """
        saved_ids = []
        failed_count = 0
        
        with transaction.atomic():
            for question in questions:
                try:
                    # 获取知识点
                    kp_id = question.get('knowledge_point_id')
                    try:
                        knowledge_point = KnowledgePoint.objects.get(id=kp_id)
                    except KnowledgePoint.DoesNotExist:
                        # 如果知识点不存在，跳过该题目
                        failed_count += 1
                        continue
                    
                    # 准备答案模板 - 可能是列表或字符串
                    answer_template = question.get('answer_template')
                    if isinstance(answer_template, list):
                        answer_template = json.dumps(answer_template, ensure_ascii=False)
                    
                    # 创建习题对象 - 移除created_by参数，因为Exercise模型中没有该字段
                    exercise = Exercise(
                        title=question.get('title', '未命名题目'),
                        content=question.get('content', ''),
                        type=question.get('type', 'other'),
                        difficulty=question.get('difficulty', 3),
                        answer_template=answer_template,
                        knowledge_point=knowledge_point
                    )
                    exercise.save()
                    saved_ids.append(exercise.id)
                    
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"保存题目到数据库时出错: {str(e)}")
                    failed_count += 1
        
        return {
            'saved_ids': saved_ids,
            'failed_count': failed_count
        }
    
    @swagger_auto_schema(
        operation_summary="导出生成的问题",
        operation_description="导出之前生成的问题为JSON或CSV格式",
        manual_parameters=[
            openapi.Parameter(
                'session_key', 
                openapi.IN_QUERY, 
                description="会话键，用于标识要导出的问题集", 
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'format', 
                openapi.IN_QUERY, 
                description="导出格式，支持'json'和'csv'", 
                type=openapi.TYPE_STRING,
                enum=['json', 'csv'],
                default='json',
                required=False
            ),
            openapi.Parameter(
                'filename', 
                openapi.IN_QUERY, 
                description="导出文件名（不含扩展名）", 
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: "成功导出问题",
            400: "错误的请求",
            404: "找不到指定的问题集"
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        导出之前生成的问题为指定格式
        """
        # 1. 获取请求参数
        session_key = request.query_params.get('session_key')
        export_format = request.query_params.get('format', 'json').lower()
        filename = request.query_params.get('filename')
        
        # 2. 验证会话键
        if not session_key:
            return create_api_response(
                success=False,
                error_code="MISSING_PARAMETER",
                message="缺少必需参数: session_key",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. 从会话中获取问题数据
        session_data = request.session.get(session_key)
        if not session_data or 'questions' not in session_data:
            return create_api_response(
                success=False,
                error_code="NOT_FOUND",
                message="找不到指定的问题集，可能已过期或不存在",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        questions = session_data['questions']
        
        # 4. 验证导出格式
        if export_format not in ['json', 'csv']:
            return create_api_response(
                success=False,
                error_code="INVALID_FORMAT",
                message=f"不支持的导出格式: {export_format}，支持的格式: json, csv",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 5. 生成默认文件名（如果未提供）
        if not filename:
            # 基于知识点和题型生成有意义的文件名
            knowledge_point_ids = session_data.get('knowledge_point_ids', [])
            question_types = session_data.get('question_types', [])
            
            # 使用时间戳确保唯一性
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # 组合文件名
            if knowledge_point_ids and len(knowledge_point_ids) <= 3:
                kp_part = f"kp{'_'.join(str(kp_id) for kp_id in knowledge_point_ids[:3])}"
            else:
                kp_part = f"kp_multi"
                
            if question_types and len(question_types) <= 2:
                type_part = f"{'_'.join(t[:3] for t in question_types[:2])}"
            else:
                type_part = "multi_types"
                
            filename = f"questions_{kp_part}_{type_part}_{timestamp}"
        
        # 6. 导出问题
        try:
            # 导入导出工具
            from ai_services.services.question_export import QuestionExporter
            
            # 调用导出功能
            return QuestionExporter.export_questions(
                questions=questions,
                format_type=export_format,
                filename=filename
            )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"导出问题时出错: {str(e)}")
            
            return create_api_response(
                success=False,
                error_code="EXPORT_ERROR",
                message=f"导出问题时出错: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExerciseViewSet(viewsets.ModelViewSet):
    """练习题视图集，支持CRUD操作"""
    queryset = Exercise.objects.all().order_by('-created_at')
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
