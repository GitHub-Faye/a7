# 练习题生成API不保存数据库版本实现计划

## 需求概述
创建一个新的API端点，用于动态生成练习题，但不将其保存到数据库中。这个API将利用任务13开发的AI问题生成模块进行处理，确保生成的练习题只存在于响应中，不进行持久化存储。

## 现有项目分析
1. 已有类似功能：
   - `QuestionGenerationViewSet` - 已实现的问题生成API，但可能会存储到数据库
   - `N8nWebhookClient.generate_questions_sync` - 用于与n8n服务交互生成问题
   - `QuestionGenerationRequestData` - 请求数据模型
   - `QuestionGenerationResponseData` - 响应数据模型
   - `QuestionData` - 单个问题数据模型

2. 已有学生助手模块：
   - `StudentDialogueViewSet` - 处理学生与AI对话
   - 使用`AllowAny`权限，无需认证即可访问

## 实现方案

### 1. 创建序列化器
创建一个新的序列化器`ExerciseGenerationSerializer`，用于验证练习题生成请求：

```python
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
```

### 2. 在N8nWebhookClient中添加练习生成方法
如果尚未实现，添加`generate_exercises`和`generate_exercises_sync`方法：

```python
async def generate_exercises(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成练习题（异步方法）
    
    Args:
        request_data: 请求数据，包含查询和生成参数
        
    Returns:
        Dict[str, Any]: 生成的练习题数据
    """
    return await self.process_ai_task("exerciseGeneration", request_data)

def generate_exercises_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成练习题（同步方法）
    
    Args:
        request_data: 请求数据，包含查询和生成参数
        
    Returns:
        Dict[str, Any]: 生成的练习题数据
    """
    return asyncio.run(self.generate_exercises(request_data))
```

### 3. 创建视图集
创建一个新的视图集`ExerciseGenerationViewSet`，用于处理练习题生成请求：

```python
class ExerciseGenerationViewSet(viewsets.ViewSet):
    """练习题生成API视图集，生成练习题但不保存到数据库"""
    permission_classes = [permissions.AllowAny]  # 允许匿名访问，便于学生使用
    
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
                
            # 返回处理后的响应
            return create_api_response(
                success=True,
                data={
                    "exercises": result["questions"],
                    "session_id": result.get("session_id", session_id)
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
```

### 4. 注册API路由
在`ai_services/urls.py`中添加路由：

```python
from rest_framework.routers import DefaultRouter
from .views import StudentDialogueViewSet, ExerciseGenerationViewSet

router = DefaultRouter()
router.register(r'dialogue', StudentDialogueViewSet, basename='student-dialogue')
router.register(r'exercises-generate', ExerciseGenerationViewSet, basename='exercise-generation')

urlpatterns = [
    # 已有的URL路径...
    path('', include(router.urls)),
]
```

### 5. 添加单元测试
创建测试文件`ai_services/tests/test_exercise_generation.py`：

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from courses.models import KnowledgePoint, Course
from users.models import User

class ExerciseGenerationAPITests(TestCase):
    """练习题生成API测试"""

    def setUp(self):
        # 创建测试数据
        self.client = APIClient()
        
        # 创建测试课程和知识点
        self.teacher = User.objects.create_user(username='teacher1', password='password123')
        self.course = Course.objects.create(
            title="测试课程", 
            description="测试课程描述",
            subject="测试学科",
            grade_level="测试年级",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="测试知识点",
            content="测试知识点内容",
            importance=5
        )
        
        # API端点
        self.url = reverse('exercise-generation-list')
    
    @patch('ai_services.views.N8nWebhookClient')
    def test_exercise_generation_success(self, mock_client):
        """测试成功生成练习题"""
        # 模拟客户端返回
        mock_instance = mock_client.return_value
        mock_instance.generate_exercises_sync.return_value = {
            "questions": [
                {
                    "title": "测试题目1",
                    "content": "这是一道测试题目",
                    "type": "single_choice",
                    "difficulty": 3,
                    "answer_template": ["选项A", "选项B", "选项C", "选项D"],
                    "knowledge_point_id": self.knowledge_point.id
                }
            ],
            "session_id": "test-session-id"
        }
        
        # 发送请求
        data = {
            "query": "测试题目生成",
            "knowledge_point_ids": [self.knowledge_point.id],
            "quantity": 1
        }
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['exercises']), 1)
        self.assertIn('session_id', response.data['data'])
        
        # 验证调用
        mock_instance.generate_exercises_sync.assert_called_once()
        call_args = mock_instance.generate_exercises_sync.call_args[0][0]
        self.assertEqual(call_args['query'], "测试题目生成")
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_exercise_generation_error(self, mock_client):
        """测试生成练习题失败的情况"""
        # 模拟客户端抛出异常
        from ai_services.services.n8n_webhook.exceptions import N8nWebhookError
        mock_instance = mock_client.return_value
        mock_instance.generate_exercises_sync.side_effect = N8nWebhookError("测试错误")
        
        # 发送请求
        data = {"query": "测试题目生成"}
        response = self.client.post(self.url, data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], "N8N_WEBHOOK_ERROR")
        
    def test_exercise_generation_invalid_params(self):
        """测试无效参数情况"""
        # 发送请求 - 缺少必需参数
        response = self.client.post(self.url, {}, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], "VALIDATION_ERROR")
```

### 6. 更新TASK模型注册
在`formats.py`中的TASK_FORMATS注册中确认已有练习生成任务类型：

```python
TASK_FORMATS: Dict[str, Dict[str, Any]] = {
    # 已有的任务类型...
    "exerciseGeneration": {
        "request": ExerciseGenerationRequestData,
        "response": ExerciseGenerationResponseData,
    },
}
```

## 测试计划
1. 单元测试：验证视图集和序列化器的功能
2. 集成测试：验证与n8n服务的交互
3. 功能测试：验证API接口是否正确生成练习题，不保存到数据库

## 文档更新
完成后需要更新API文档，包括:
1. 添加新API端点的详细说明
2. 提供示例请求和响应
3. 说明与已有问题生成API的区别（不保存数据库）
