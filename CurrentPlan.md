
from ai_services.services.n8n_webhook.client import N8nWebhookClient
from ai_services.services.n8n_webhook.exceptions import N8nWebhookError, N8nInvalidRequestError
from ai_services.services.knowledge_converter import create_course_with_knowledge_points
from ai_services.api_response import create_api_response
```

### 4. 编写单元测试

在`a7/courses/tests_api_new.py`中添加对`CourseContentGenerationView`的测试：

```python
# a7/courses/tests_api_new.py
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, Role
from .models import Course, KnowledgePoint

class CourseContentGenerationAPITests(APITestCase):
    """测试课程内容生成API"""
    
    def setUp(self):
        # 创建教师角色和用户
        self.teacher_role = Role.objects.create(name='teacher')
        self.teacher = User.objects.create_user(
            username='teacher1', 
            password='password123',
            email='teacher1@example.com'
        )
        self.teacher.roles.add(self.teacher_role)
        
        # 创建学生角色和用户
        self.student_role = Role.objects.create(name='student')
        self.student = User.objects.create_user(
            username='student1', 
            password='password123',
            email='student1@example.com'
        )
        self.student.roles.add(self.student_role)
        
        # API端点
        self.url = reverse('course-generate-content')
        
        # 有效的请求数据
        self.valid_data = {
            'course_name': 'Python编程基础',
            'chapter_count': 5,
            'course_description': '入门级Python编程课程，涵盖基础语法和简单应用',
            'subject': '计算机科学',
            'grade_level': '大学一年级',
            'additional_requirements': '包含实践练习'
        }
    
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.process_ai_task_sync')
    def test_generate_course_content_success(self, mock_process):
        """测试成功生成课程内容"""
        # 模拟AI服务响应
        mock_response = {
            'course': {
                'title': 'Python编程基础',
                'description': '入门级Python编程课程，涵盖基础语法和简单应用',
                'subject': '计算机科学',
                'grade_level': '大学一年级'
            },
            'knowledge_points': [
                {
                    'title': '第一章：Python简介',
                    'content': 'Python的历史和特点',
                    'importance': 8,
                    'children': [
                        {
                            'title': 'Python的历史',
                            'content': 'Python的发展历程',
                            'importance': 5
                        }
                    ]
                }
            ]
        }
        mock_process.return_value = mock_response
        
        # 登录教师用户
        self.client.login(username='teacher1', password='password123')
        
        # 发送请求
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], '课程内容生成成功')
        
        # 验证调用参数
        mock_process.assert_called_once_with('courseGeneration', self.valid_data)
        
        # 验证数据库记录
        self.assertEqual(Course.objects.count(), 1)
        course = Course.objects.first()
        self.assertEqual(course.title, 'Python编程基础')
        self.assertEqual(course.teacher, self.teacher)
        
        # 验证知识点创建
        self.assertEqual(KnowledgePoint.objects.count(), 2)  # 1个父知识点和1个子知识点
        
    def test_generate_course_content_unauthorized(self):
        """测试未授权用户无法生成课程内容"""
        # 使用学生用户登录
        self.client.login(username='student1', password='password123')
        
        # 发送请求
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # 验证响应（应该被拒绝）
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_generate_course_content_invalid_data(self):
        """测试无效数据的处理"""
        # 登录教师用户
        self.client.login(username='teacher1', password='password123')
        
        # 发送缺少必要字段的请求
        invalid_data = {
            'course_name': 'Python编程基础',
            # 缺少chapter_count和其他必要字段
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')
        
    @patch('ai_services.services.n8n_webhook.client.N8nWebhookClient.process_ai_task_sync')
    def test_generate_course_content_ai_service_error(self, mock_process):
        """测试AI服务错误的处理"""
        # 模拟AI服务错误
        mock_process.side_effect = N8nWebhookError("AI服务暂时不可用")
        
        # 登录教师用户
        self.client.login(username='teacher1', password='password123')
        
        # 发送请求
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'AI_SERVICE_ERROR')
```

## 测试计划

1. **单元测试**：
   - 实现上述`CourseContentGenerationAPITests`测试类
   - 测试成功场景、未授权访问、无效数据和AI服务错误情况

2. **集成测试**：
   - 测试与真实n8n服务的集成（可选，依赖于n8n服务的可用性）
   - 测试完整的课程生成流程，从API请求到数据库存储

3. **手动测试**：
   - 使用Swagger UI或Postman发送请求到`/api/courses/generate-content/`端点
   - 验证生成的课程和知识点在数据库中正确创建
   - 测试各种错误情况的响应

## 实施步骤

1. 在`a7/courses/serializers.py`中添加`CourseGenerationSerializer`
2. 更新`a7/courses/views.py`中的导入语句
3. 重构`CourseContentGenerationView`视图
4. 添加单元测试
5. 运行测试验证功能
6. 手动测试API端点

## 注意事项

1. 确保事务管理正确，避免部分成功导致数据不一致
2. 提供详细的错误信息，便于调试和用户理解
3. 限制章节数量，避免过大的请求导致性能问题
4. 考虑添加异步处理选项，处理可能的长时间运行任务
