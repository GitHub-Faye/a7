from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Course
from users.models import User, Role
import json

class CourseAPITests(TestCase):
    """测试课程API的功能"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建一个角色 
        self.admin_role = Role.objects.create(name='admin', description='管理员角色')
        self.teacher_role = Role.objects.create(name='teacher', description='教师角色')
        self.student_role = Role.objects.create(name='student', description='学生角色')
        
        # 创建测试用户
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='adminpass',
            role='admin',
            is_staff=True
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher', 
            email='teacher@example.com', 
            password='teacherpass',
            role='teacher'
        )
        
        self.student_user = User.objects.create_user(
            username='student', 
            email='student@example.com', 
            password='studentpass',
            role='student'
        )
        
        # 创建一个测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='计算机科学',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 初始化API客户端
        self.client = APIClient()
    
    def test_list_courses(self):
        """测试获取课程列表"""
        # 1. 未认证用户无法访问
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 认证用户可以访问
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 验证课程数据
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], '测试课程')
    
    def test_retrieve_course(self):
        """测试获取单个课程"""
        # 认证用户可以获取课程详情
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        
        # 验证课程数据
        course_data = response.data['data']
        self.assertEqual(course_data['title'], '测试课程')
        self.assertEqual(course_data['subject'], '计算机科学')
    
    def test_create_course(self):
        """测试创建课程"""
        url = reverse('course-list')
        data = {
            'title': '新课程',
            'description': '这是一个新课程',
            'subject': '数学',
            'grade_level': '初中'
        }
        
        # 1. 未认证用户无法创建
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 学生无法创建课程
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 教师可以创建课程
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的课程
        self.assertEqual(Course.objects.count(), 2)
        new_course = Course.objects.get(title='新课程')
        self.assertEqual(new_course.subject, '数学')
        self.assertEqual(new_course.teacher, self.teacher_user)
        
        # 4. 管理员也可以创建课程
        data['title'] = '管理员课程'
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的课程
        self.assertEqual(Course.objects.count(), 3)
    
    def test_update_course(self):
        """测试更新课程"""
        url = reverse('course-detail', args=[self.course.id])
        data = {
            'title': '更新后的课程',
            'description': '这是更新后的描述',
            'subject': '计算机科学',
            'grade_level': '高中'
        }
        
        # 1. 学生无法更新课程
        self.client.force_authenticate(user=self.student_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. 其他教师无法更新课程
        another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        self.client.force_authenticate(user=another_teacher)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 课程创建者可以更新课程
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新后的课程
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, '更新后的课程')
        self.assertEqual(self.course.description, '这是更新后的描述')
        
        # 4. 管理员可以更新任何课程
        data['title'] = '管理员更新的课程'
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新后的课程
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, '管理员更新的课程')
    
    def test_delete_course(self):
        """测试删除课程"""
        url = reverse('course-detail', args=[self.course.id])
        
        # 1. 学生无法删除课程
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. 其他教师无法删除课程
        another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        self.client.force_authenticate(user=another_teacher)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 创建更多测试课程
        course2 = Course.objects.create(
            title='测试课程2',
            description='这是第二个测试课程',
            subject='物理',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 4. 课程创建者可以删除课程
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(reverse('course-detail', args=[course2.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证课程已删除
        self.assertEqual(Course.objects.filter(id=course2.id).count(), 0)
        
        # 5. 管理员可以删除任何课程
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证课程已删除
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 0)
    
    def test_my_courses(self):
        """测试获取当前用户创建的课程列表"""
        # 教师创建多个课程
        Course.objects.create(
            title='教师课程1',
            description='这是教师的第一个课程',
            subject='语文',
            grade_level='初中',
            teacher=self.teacher_user
        )
        Course.objects.create(
            title='教师课程2',
            description='这是教师的第二个课程',
            subject='英语',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 另一个教师创建课程
        another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        Course.objects.create(
            title='另一个教师的课程',
            description='这是另一个教师的课程',
            subject='历史',
            grade_level='高中',
            teacher=another_teacher
        )
        
        # 测试获取自己的课程列表
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(reverse('course-my-courses'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 验证课程数据
        results = response.data['data']['results']
        self.assertEqual(len(results), 3)
        
        # 验证返回的课程标题
        titles = [item['title'] for item in results]
        self.assertIn('测试课程', titles)
        self.assertIn('教师课程1', titles)
        self.assertIn('教师课程2', titles)
        self.assertNotIn('另一个教师的课程', titles) 