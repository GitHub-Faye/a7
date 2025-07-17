from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import tempfile
import os
import shutil
from courses.models import Course, Courseware, CoursewareFile, CourseProgress
from django.core.files.uploadedfile import SimpleUploadedFile
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

User = get_user_model()

class CoursewareFileDownloadTest(TestCase):
    """测试课件文件下载API"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 添加调试信息
        print("\n===== 设置测试环境 =====")
        
        # 创建测试用户
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpassword'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher', 
            email='teacher@example.com', 
            password='teacherpassword'
        )
        self.student_user = User.objects.create_user(
            username='student', 
            email='student@example.com', 
            password='studentpassword'
        )
        self.unauthorized_user = User.objects.create_user(
            username='unauthorized', 
            email='unauthorized@example.com', 
            password='password'
        )
        
        print(f"创建用户: admin={self.admin_user.id}, teacher={self.teacher_user.id}, student={self.student_user.id}")
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='测试课程描述',
            subject='测试学科',
            grade_level='测试年级',
            teacher=self.teacher_user
        )
        
        print(f"创建课程: id={self.course.id}, title={self.course.title}")
        
        # 使用CourseProgress关联学生和课程
        print("使用CourseProgress关联学生和课程")
        self.course_progress = CourseProgress.objects.create(
            student=self.student_user,
            course=self.course,
            overall_progress=50.0  # 设置一些进度
        )
        print(f"创建课程进度: student={self.student_user.id}, course={self.course.id}")
        
        # 创建测试课件
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='测试课件',
            content='测试课件内容',
            type='document',
            created_by=self.teacher_user
        )
        
        print(f"创建课件: id={self.courseware.id}, title={self.courseware.title}")
        
        # 创建测试文件
        self.test_file_content = b'Test file content'
        self.test_file = SimpleUploadedFile(
            name='test_file.txt',
            content=self.test_file_content,
            content_type='text/plain'
        )
        
        # 创建课件文件记录
        self.courseware_file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=self.test_file
        )
        
        print(f"创建课件文件: id={self.courseware_file.id}, name={self.courseware_file.file_name}")
        
        # 设置API客户端
        self.client = APIClient()
        
    def tearDown(self):
        """清理测试环境"""
        # 删除测试目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # 确保关闭所有可能打开的文件句柄
        for courseware_file in CoursewareFile.objects.all():
            if courseware_file.file and hasattr(courseware_file.file, 'close'):
                try:
                    courseware_file.file.close()
                except:
                    pass
        
        # 删除上传的测试文件
        for courseware_file in CoursewareFile.objects.all():
            if courseware_file.file and os.path.exists(courseware_file.file.path):
                try:
                    os.remove(courseware_file.file.path)
                except PermissionError:
                    print(f"警告: 无法删除文件 {courseware_file.file.path}，可能被其他进程占用")
    
    def test_download_file_as_admin(self):
        """测试管理员下载文件"""
        # 登录管理员用户
        self.client.force_authenticate(user=self.admin_user)
        
        # 发送下载请求
        url = reverse('courseware-download', args=[self.courseware_file.id])
        print(f"\n测试管理员下载文件: {url}")
        response = self.client.get(url)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查Content-Disposition头，但不检查具体文件名（可能包含随机ID）
        self.assertIn('attachment; filename=', response.get('Content-Disposition', ''))
    
    def test_download_file_as_teacher(self):
        """测试教师下载文件"""
        # 登录教师用户
        self.client.force_authenticate(user=self.teacher_user)
        
        # 发送下载请求
        url = reverse('courseware-download', args=[self.courseware_file.id])
        print(f"\n测试教师下载文件: {url}")
        response = self.client.get(url)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查Content-Disposition头，但不检查具体文件名（可能包含随机ID）
        self.assertIn('attachment; filename=', response.get('Content-Disposition', ''))
    
    def test_download_file_as_student(self):
        """测试学生下载文件"""
        # 登录学生用户
        self.client.force_authenticate(user=self.student_user)
        
        # 发送下载请求
        url = reverse('courseware-download', args=[self.courseware_file.id])
        print(f"\n测试学生下载文件: {url}")
        response = self.client.get(url)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查Content-Disposition头，但不检查具体文件名（可能包含随机ID）
        self.assertIn('attachment; filename=', response.get('Content-Disposition', ''))
    
    def test_download_file_as_unauthorized_user(self):
        """测试未授权用户下载文件"""
        # 登录未授权用户
        self.client.force_authenticate(user=self.unauthorized_user)
        
        # 发送下载请求
        url = reverse('courseware-download', args=[self.courseware_file.id])
        print(f"\n测试未授权用户下载文件: {url}")
        response = self.client.get(url)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_download_file_unauthenticated(self):
        """测试未登录用户下载文件"""
        # 确保客户端未认证
        self.client.force_authenticate(user=None)
        
        # 发送下载请求
        url = reverse('courseware-download', args=[self.courseware_file.id])
        print(f"\n测试未登录用户下载文件: {url}")
        response = self.client.get(url)
        
        # 验证响应 (应该重定向到登录页面或返回401未授权)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_download_nonexistent_file(self):
        """测试下载不存在的文件"""
        # 登录管理员用户
        self.client.force_authenticate(user=self.admin_user)
        
        # 发送下载请求 (使用不存在的ID)
        url = reverse('courseware-download', args=[99999])
        print(f"\n测试下载不存在的文件: {url}")
        response = self.client.get(url)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 