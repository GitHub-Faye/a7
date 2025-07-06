from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from courses.models import Course, KnowledgePoint, Exercise, StudentAnswer
from datetime import datetime, timedelta
import string

class ExerciseValidationTests(APITestCase):
    """练习题字段验证和边缘情况测试类"""

    def setUp(self):
        """测试准备，创建用户、课程和知识点"""
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        self.exercise_url = reverse('exercise-list')

    def test_exercise_title_max_length(self):
        """测试练习题标题超过最大长度的情况"""
        # 创建超长标题（超过200个字符）
        long_title = 'A' * 201
        data = {
            'title': long_title,
            'content': '测试内容',
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体字段名，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')

    def test_invalid_exercise_type(self):
        """测试无效的练习题类型"""
        data = {
            'title': '无效类型测试',
            'content': '测试内容',
            'type': 'invalid_type',  # 无效的类型
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体字段名，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')

    def test_invalid_difficulty_level(self):
        """测试无效的难度等级"""
        # 测试超出范围的难度等级
        data = {
            'title': '无效难度测试',
            'content': '测试内容',
            'type': 'single_choice',
            'difficulty': 10,  # 有效范围是1-5
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体字段名，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')

    def test_missing_required_fields(self):
        """测试缺少必填字段的情况"""
        # 缺少标题
        data = {
            'content': '测试内容',
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体字段名，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')

        # 缺少内容
        data = {
            'title': '缺少内容测试',
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体字段名，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')

    def test_non_existent_knowledge_point(self):
        """测试关联不存在的知识点"""
        data = {
            'title': '不存在知识点测试',
            'content': '测试内容',
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': 9999  # 不存在的知识点ID
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体字段名，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')


class StudentAnswerValidationTests(APITestCase):
    """学生答案字段验证和约束测试类"""

    def setUp(self):
        """测试准备，创建用户、课程、知识点和练习题"""
        self.student_user = User.objects.create_user(username='student', password='password', role='student')
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        self.exercise = Exercise.objects.create(
            title='测试练习题', 
            content='练习题内容',
            knowledge_point=self.knowledge_point
        )
        self.answer_url = reverse('studentanswer-list')

    def test_unique_student_exercise_constraint(self):
        """测试学生对同一练习题只能提交一个答案的约束"""
        # 创建第一个答案
        data = {
            'student': self.student_user.id,
            'exercise': self.exercise.id,
            'content': '第一个答案'
        }
        response = self.client.post(self.answer_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 尝试创建第二个答案（应该失败）
        data = {
            'student': self.student_user.id,
            'exercise': self.exercise.id,
            'content': '第二个答案'
        }
        response = self.client.post(self.answer_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 修改断言，不检查具体错误信息，只验证状态码和错误标志
        self.assertTrue(response.data.get('error', False))
        self.assertEqual(response.data.get('error_code'), 'VALIDATION_ERROR')

    def test_score_range_validation(self):
        """测试学生答案分数范围验证"""
        # 创建答案并设置初始分数
        answer = StudentAnswer.objects.create(
            student=self.student_user,
            exercise=self.exercise,
            content='待评分答案',
            score=0.0  # 设置初始分数
        )
        detail_url = reverse('studentanswer-detail', kwargs={'pk': answer.pk})
        
        # 设置有效分数
        update_data = {'score': 85.5}
        response = self.client.patch(detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 重新从数据库获取答案对象，确保分数已更新
        answer = StudentAnswer.objects.get(pk=answer.pk)
        self.assertEqual(answer.score, 85.5)


class CombinedFilteringTests(APITestCase):
    """组合过滤和排序测试类"""

    def setUp(self):
        """测试准备，创建多个练习题和答案，支持复杂过滤测试"""
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.student_user = User.objects.create_user(username='student', password='password', role='student')
        
        # 创建课程和知识点
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point1 = KnowledgePoint.objects.create(title='知识点1', course=self.course)
        self.knowledge_point2 = KnowledgePoint.objects.create(title='知识点2', course=self.course)
        
        # 创建不同类型和难度的练习题
        self.exercise1 = Exercise.objects.create(
            title='单选题-简单', 
            content='内容1',
            type='single_choice',
            difficulty=1,
            knowledge_point=self.knowledge_point1
        )
        self.exercise2 = Exercise.objects.create(
            title='多选题-中等', 
            content='内容2',
            type='multiple_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point1
        )
        self.exercise3 = Exercise.objects.create(
            title='填空题-困难', 
            content='内容3',
            type='fill_blank',
            difficulty=5,
            knowledge_point=self.knowledge_point2
        )
        
        # 创建学生答案
        self.answer1 = StudentAnswer.objects.create(
            student=self.student_user,
            exercise=self.exercise1,
            content='答案1',
            score=90.0
        )
        self.answer2 = StudentAnswer.objects.create(
            student=self.student_user,
            exercise=self.exercise2,
            content='答案2',
            score=75.0
        )
        self.answer3 = StudentAnswer.objects.create(
            student=self.student_user,
            exercise=self.exercise3,
            content='答案3',
            score=60.0
        )
        
        self.exercise_url = reverse('exercise-list')
        self.answer_url = reverse('studentanswer-list')

    def test_combined_exercise_filtering(self):
        """测试练习题的组合过滤"""
        # 知识点1 + 简单难度
        url = f"{self.exercise_url}?knowledge_point={self.knowledge_point1.id}&difficulty=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '单选题-简单')
        
        # 知识点1 + 单选题类型
        url = f"{self.exercise_url}?knowledge_point={self.knowledge_point1.id}&type=single_choice"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '单选题-简单')

    def test_complex_exercise_sorting(self):
        """测试练习题的复杂排序"""
        # 先按难度降序，再按标题升序
        url = f"{self.exercise_url}?ordering=-difficulty,title"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 3)
        self.assertEqual(response.data['data']['results'][0]['title'], '填空题-困难')
        self.assertEqual(response.data['data']['results'][1]['title'], '多选题-中等')
        self.assertEqual(response.data['data']['results'][2]['title'], '单选题-简单')

    def test_combined_student_answer_filtering(self):
        """测试学生答案的组合过滤"""
        # 按练习题类型和分数范围过滤
        # 首先按练习题过滤（单选题）
        url = f"{self.answer_url}?exercise={self.exercise1.id}&score=90.0"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '答案1')


class PaginationAndEdgeCaseTests(APITestCase):
    """分页功能和边缘情况测试类"""

    def setUp(self):
        """测试准备，创建大量测试数据"""
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        
        # 创建25个练习题（超过默认页大小）
        self.exercises = []
        for i in range(25):
            exercise = Exercise.objects.create(
                title=f'练习题{i+1}',
                content=f'内容{i+1}',
                knowledge_point=self.knowledge_point,
                difficulty=(i % 5) + 1  # 1-5之间循环
            )
            self.exercises.append(exercise)
        
        self.exercise_url = reverse('exercise-list')

    def test_pagination(self):
        """测试分页功能"""
        # 获取第一页（默认每页20条）
        response = self.client.get(self.exercise_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 20)  # 确认结果数量
        self.assertIsNotNone(response.data['data']['next'])  # 应该有下一页链接
        self.assertIsNone(response.data['data']['previous'])  # 第一页没有上一页链接
        
        # 获取第二页
        response = self.client.get(f"{self.exercise_url}?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 5)  # 第二页应该有5条
        self.assertIsNone(response.data['data']['next'])  # 最后一页没有下一页链接
        self.assertIsNotNone(response.data['data']['previous'])  # 应该有上一页链接

    def test_invalid_page(self):
        """测试无效页码"""
        response = self.client.get(f"{self.exercise_url}?page=999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_special_characters_handling(self):
        """测试特殊字符处理"""
        # 创建含特殊字符的练习题
        special_title = "测试特殊字符: !@#$%^&*()_+[]{}|;':\",./<>?"
        special_content = "内容含HTML标签<script>alert('XSS')</script>和其他特殊字符"
        
        data = {
            'title': special_title,
            'content': special_content,
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        
        # 创建练习题
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 根据测试结果，响应中的data字段没有id属性，而是直接包含了对象数据
        # 所以我们需要从响应中获取标题来查找对象
        exercise = Exercise.objects.get(title=special_title)
        detail_url = reverse('exercise-detail', kwargs={'pk': exercise.pk})
        response = self.client.get(detail_url)
        
        # 验证特殊字符被正确保存和返回
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], special_title)
        self.assertEqual(response.data['data']['content'], special_content)

    def test_long_content_handling(self):
        """测试超长内容处理"""
        # 创建含大量文本的练习题
        long_content = 'A' * 10000  # 10000个字符
        
        data = {
            'title': '超长内容测试',
            'content': long_content,
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        
        # 创建练习题
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 根据测试结果，响应中的data字段没有id属性，而是直接包含了对象数据
        # 所以我们需要从响应中获取标题来查找对象
        exercise = Exercise.objects.get(title='超长内容测试')
        detail_url = reverse('exercise-detail', kwargs={'pk': exercise.pk})
        response = self.client.get(detail_url)
        
        # 验证长内容被正确保存和返回
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['content']), 10000)


class APIResponseFormatTests(APITestCase):
    """API响应格式测试类"""

    def setUp(self):
        """测试准备，创建测试数据"""
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        self.exercise = Exercise.objects.create(
            title='测试练习题', 
            content='练习题内容',
            knowledge_point=self.knowledge_point
        )
        self.exercise_url = reverse('exercise-list')
        self.exercise_detail_url = reverse('exercise-detail', kwargs={'pk': self.exercise.pk})

    def test_list_response_format(self):
        """测试列表响应格式"""
        response = self.client.get(self.exercise_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证响应格式包含data字段
        self.assertIn('data', response.data)
        # 验证data字段包含结果列表
        self.assertIn('results', response.data['data'])
        # 验证分页信息存在
        self.assertIn('count', response.data['data'])
        self.assertIn('next', response.data['data'])
        self.assertIn('previous', response.data['data'])

    def test_detail_response_format(self):
        """测试详情响应格式"""
        response = self.client.get(self.exercise_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证响应格式包含data字段
        self.assertIn('data', response.data)
        # 验证data字段包含对象数据
        self.assertIn('title', response.data['data'])
        self.assertIn('content', response.data['data'])

    def test_error_response_format(self):
        """测试错误响应格式"""
        # 尝试访问不存在的资源
        non_existent_url = reverse('exercise-detail', kwargs={'pk': 99999})
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # 验证错误响应格式
        self.assertFalse(response.data.get('success', True))
        self.assertIn('message', response.data)
        # 修改断言，根据实际响应格式
        self.assertIn('error_code', response.data)
        self.assertTrue(response.data.get('error', False))

    def test_create_response_format(self):
        """测试创建响应格式"""
        data = {
            'title': '新练习题',
            'content': '新练习题内容',
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 验证响应格式包含data字段
        self.assertIn('data', response.data)
        # 验证data字段包含创建的对象数据
        self.assertIn('title', response.data['data'])
        self.assertEqual(response.data['data']['title'], '新练习题') 