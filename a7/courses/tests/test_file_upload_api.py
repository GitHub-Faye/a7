import os
import json
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course, Courseware, CoursewareFile
from users.models import User, Role

class FileUploadAPITest(TestCase):
    """测试文件上传API"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户和角色
        self.teacher_role, _ = Role.objects.get_or_create(name='teacher')
        self.student_role, _ = Role.objects.get_or_create(name='student')
        
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password123'
        )
        # 设置用户角色
        self.teacher.role = 'teacher'
        self.teacher.role_obj = self.teacher_role
        self.teacher.save()
        
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='password123'
        )
        # 设置用户角色
        self.student.role = 'student'
        self.student.role_obj = self.student_role
        self.student.save()
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            teacher=self.teacher,
            subject='计算机科学',
            grade_level='大学'
        )
        
        # 创建测试课件
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='测试课件',
            content='这是测试课件内容',
            type='document',
            created_by=self.teacher
        )
        
        # 设置API客户端
        self.client = APIClient()
        
    def test_upload_file_success(self):
        """测试成功上传文件"""
        # 登录教师账号
        self.client.force_authenticate(user=self.teacher)
        
        # 创建测试文件
        test_file = SimpleUploadedFile(
            name='test.pdf',
            content=b'test file content',
            content_type='application/pdf'
        )
        
        # 发送请求
        url = reverse('courseware-upload')
        data = {
            'courseware_id': self.courseware.id,
            'file': test_file
        }
        response = self.client.post(url, data, format='multipart')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('file_name', response.data['data'])
        self.assertEqual(response.data['data']['file_name'], 'test.pdf')
        
        # 验证文件是否已保存到数据库
        self.assertTrue(CoursewareFile.objects.filter(courseware=self.courseware).exists())
        
    def test_upload_invalid_file_type(self):
        """测试上传无效文件类型"""
        # 登录教师账号
        self.client.force_authenticate(user=self.teacher)
        
        # 创建测试文件（使用不支持的文件类型）
        test_file = SimpleUploadedFile(
            name='test.exe',
            content=b'test file content',
            content_type='application/octet-stream'
        )
        
        # 发送请求
        url = reverse('courseware-upload')
        data = {
            'courseware_id': self.courseware.id,
            'file': test_file
        }
        response = self.client.post(url, data, format='multipart')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)
        
    def test_upload_file_without_permission(self):
        """测试无权限上传文件"""
        # 登录学生账号（学生无权上传）
        self.client.force_authenticate(user=self.student)
        
        # 创建测试文件
        test_file = SimpleUploadedFile(
            name='test.pdf',
            content=b'test file content',
            content_type='application/pdf'
        )
        
        # 发送请求
        url = reverse('courseware-upload')
        data = {
            'courseware_id': self.courseware.id,
            'file': test_file
        }
        response = self.client.post(url, data, format='multipart')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_upload_file_to_nonexistent_courseware(self):
        """测试上传文件到不存在的课件"""
        # 登录教师账号
        self.client.force_authenticate(user=self.teacher)
        
        # 创建测试文件
        test_file = SimpleUploadedFile(
            name='test.pdf',
            content=b'test file content',
            content_type='application/pdf'
        )
        
        # 发送请求（使用不存在的课件ID）
        url = reverse('courseware-upload')
        data = {
            'courseware_id': 9999,  # 不存在的ID
            'file': test_file
        }
        response = self.client.post(url, data, format='multipart')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)
        
    def test_upload_file_missing_parameters(self):
        """测试上传文件缺少参数"""
        # 登录教师账号
        self.client.force_authenticate(user=self.teacher)
        
        # 发送请求（缺少文件参数）
        url = reverse('courseware-upload')
        data = {
            'courseware_id': self.courseware.id
            # 缺少 'file' 参数
        }
        response = self.client.post(url, data, format='multipart')
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data) 