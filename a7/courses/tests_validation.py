from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from .models import Course, KnowledgePoint, Courseware

class CourseApiValidationTests(TestCase):
    """测试课程API验证逻辑"""

    def setUp(self):
        # 创建测试用户
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password',
            is_staff=True
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='password'
        )
        self.teacher_user.role = 'teacher'
        self.teacher_user.save()
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            subject='Math',
            grade_level='Grade 10',
            teacher=self.teacher_user
        )
        
        # 设置API客户端并登录
        self.client = APIClient()
        
    def test_course_title_validation(self):
        """测试课程标题验证"""
        # 确保用户有足够的权限
        self.teacher_user.is_staff = True
        self.teacher_user.save()
        
        self.client.force_authenticate(user=self.teacher_user)
        
        # 测试空标题
        response = self.client.post(reverse('course-list'), {
            'title': '',
            'description': 'Test Description',
            'subject': 'Math',
            'grade_level': 'Grade 10'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.content))
        
        # 测试标题太短
        response = self.client.post(reverse('course-list'), {
            'title': 'AB',  # 少于3个字符
            'description': 'Test Description',
            'subject': 'Math',
            'grade_level': 'Grade 10'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 测试标题重复
        response = self.client.post(reverse('course-list'), {
            'title': 'Test Course',  # 重复标题
            'description': 'Another Description',
            'subject': 'Science',
            'grade_level': 'Grade 9'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.content))
        
        # 测试有效标题
        response = self.client.post(reverse('course-list'), {
            'title': 'New Valid Course',
            'description': 'Valid Description',
            'subject': 'Physics',
            'grade_level': 'Grade 11'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_course_update_validation(self):
        """测试课程更新验证"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # 创建另一个课程用于测试重复标题
        Course.objects.create(
            title='Another Course',
            description='Another Description',
            subject='Science',
            grade_level='Grade 9',
            teacher=self.teacher_user
        )
        
        # 测试更新为重复标题
        response = self.client.put(
            reverse('course-detail', kwargs={'pk': self.course.id}), 
            {
                'title': 'Another Course',  # 已存在的标题
                'description': 'Updated Description',
                'subject': 'Updated Math',
                'grade_level': 'Grade 12'
            }, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.content))
        
        # 测试更新为有效数据
        response = self.client.put(
            reverse('course-detail', kwargs={'pk': self.course.id}), 
            {
                'title': 'Updated Course Title',
                'description': 'Updated Description',
                'subject': 'Updated Math',
                'grade_level': 'Grade 12'
            }, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Course.objects.get(id=self.course.id).title, 'Updated Course Title')
        

class KnowledgePointApiValidationTests(TestCase):
    """测试知识点API验证逻辑"""

    def setUp(self):
        # 创建测试用户
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='password'
        )
        self.teacher_user.role = 'teacher'
        self.teacher_user.is_staff = True  # 添加权限
        self.teacher_user.save()
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            subject='Math',
            grade_level='Grade 10',
            teacher=self.teacher_user
        )
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            title='Test Knowledge Point',
            content='Test Content',
            importance=5,
            course=self.course,
            parent=None
        )
        
        # 设置API客户端并登录
        self.client = APIClient()
        self.client.force_authenticate(user=self.teacher_user)
        
    def test_knowledge_point_importance_validation(self):
        """测试知识点重要性验证"""
        # 测试低于范围的重要性
        response = self.client.post(reverse('knowledge-point-list'), {
            'title': 'New Knowledge Point',
            'content': 'New Content',
            'importance': 0,  # 低于范围(1-10)
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('importance', str(response.content))
        
        # 测试高于范围的重要性
        response = self.client.post(reverse('knowledge-point-list'), {
            'title': 'New Knowledge Point',
            'content': 'New Content',
            'importance': 11,  # 高于范围(1-10)
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('importance', str(response.content))
        
        # 测试有效的重要性
        response = self.client.post(reverse('knowledge-point-list'), {
            'title': 'New Knowledge Point',
            'content': 'New Content',
            'importance': 8,  # 有效范围内
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_knowledge_point_parent_validation(self):
        """测试知识点父级验证"""
        # 创建另一个课程和知识点用于测试跨课程引用
        other_course = Course.objects.create(
            title='Other Course',
            description='Other Description',
            subject='Science',
            grade_level='Grade 9',
            teacher=self.teacher_user
        )
        
        other_knowledge_point = KnowledgePoint.objects.create(
            title='Other Knowledge Point',
            content='Other Content',
            importance=5,
            course=other_course,
            parent=None
        )
        
        # 测试跨课程引用
        response = self.client.post(reverse('knowledge-point-list'), {
            'title': 'Cross Course Knowledge Point',
            'content': 'Test Content',
            'importance': 5,
            'course': self.course.id,
            'parent': other_knowledge_point.id  # 来自其他课程的父知识点
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent', str(response.content))
        
        # 测试有效的父知识点
        response = self.client.post(reverse('knowledge-point-list'), {
            'title': 'Child Knowledge Point',
            'content': 'Child Content',
            'importance': 4,
            'course': self.course.id,
            'parent': self.knowledge_point.id  # 同一课程的父知识点
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_knowledge_point_cycle_validation(self):
        """测试知识点循环引用验证"""
        # 创建父子关系
        child = KnowledgePoint.objects.create(
            title='Child Knowledge Point',
            content='Child Content',
            importance=4,
            course=self.course,
            parent=self.knowledge_point
        )
        
        # 测试循环引用 - 将父级设置为其子级
        response = self.client.put(
            reverse('knowledge-point-detail', kwargs={'pk': self.knowledge_point.id}), 
            {
                'title': 'Updated Knowledge Point',
                'content': 'Updated Content',
                'importance': 6,
                'parent': child.id  # 尝试将子级设为父级，造成循环
            }, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        content = response.json()
        self.assertIn('parent', str(content))


class CoursewareApiValidationTests(TestCase):
    """测试课件API验证逻辑"""

    def setUp(self):
        # 创建测试用户
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='password'
        )
        self.teacher_user.role = 'teacher'
        self.teacher_user.is_staff = True  # 添加权限
        self.teacher_user.save()
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            subject='Math',
            grade_level='Grade 10',
            teacher=self.teacher_user
        )
        
        # 创建测试课件
        self.courseware = Courseware.objects.create(
            title='Test Courseware',
            content='Test Courseware Content',
            type='document',
            course=self.course,
            created_by=self.teacher_user
        )
        
        # 设置API客户端并登录
        self.client = APIClient()
        self.client.force_authenticate(user=self.teacher_user)
        
    def test_courseware_content_validation(self):
        """测试课件内容验证"""
        # 测试内容太短
        response = self.client.post(reverse('courseware-list'), {
            'title': 'New Courseware',
            'content': 'Short',  # 太短的内容
            'type': 'document',
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', str(response.content))
        
        # 测试有效的内容
        response = self.client.post(reverse('courseware-list'), {
            'title': 'New Courseware',
            'content': 'This is a valid content with sufficient length',
            'type': 'document',
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_courseware_type_validation(self):
        """测试课件类型验证"""
        # 测试无效类型
        response = self.client.post(reverse('courseware-list'), {
            'title': 'Invalid Type Courseware',
            'content': 'This is a test content for invalid type',
            'type': 'invalid_type',  # 无效的类型
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', str(response.content))
        
        # 测试所有有效类型
        valid_types = ['document', 'video', 'audio', 'image', 'interactive', 'other']
        for index, valid_type in enumerate(valid_types):
            response = self.client.post(reverse('courseware-list'), {
                'title': f'Valid Type Courseware {index}',
                'content': f'This is a test content for {valid_type}',
                'type': valid_type,
                'course': self.course.id
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
    def test_courseware_title_uniqueness(self):
        """测试课件标题唯一性"""
        # 测试重复标题
        response = self.client.post(reverse('courseware-list'), {
            'title': 'Test Courseware',  # 已存在的标题
            'content': 'This is a duplicate title test',
            'type': 'document',
            'course': self.course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.content))
        
        # 创建另一个课程，测试不同课程可以有相同标题的课件
        other_course = Course.objects.create(
            title='Other Course',
            description='Other Description',
            subject='Science',
            grade_level='Grade 9',
            teacher=self.teacher_user
        )
        
        response = self.client.post(reverse('courseware-list'), {
            'title': 'Test Courseware',  # 相同标题，但不同课程
            'content': 'This is a test for different course',
            'type': 'document',
            'course': other_course.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 