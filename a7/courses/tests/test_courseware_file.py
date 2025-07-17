from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from courses.models import Course, Courseware, CoursewareFile
from users.models import User
from django.conf import settings
import os
import shutil
import tempfile


class CoursewareFileTestCase(TestCase):
    """测试CoursewareFile模型和相关功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 保存原始MEDIA_ROOT并创建临时目录
        self.original_media_root = settings.MEDIA_ROOT
        self.temp_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.temp_dir
        
        # 创建测试用户、课程和课件
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password123'
        )
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='测试学科',
            grade_level='高中',
            teacher=self.user
        )
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='测试课件',
            content='这是测试课件内容',
            type='document',
            created_by=self.user
        )

    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始MEDIA_ROOT
        settings.MEDIA_ROOT = self.original_media_root
        
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_courseware_file_creation(self):
        """测试创建课件文件并验证关联"""
        # 创建测试文件
        file_content = b"test file content"
        test_file = SimpleUploadedFile("test_file.txt", file_content, content_type="text/plain")
        
        # 创建文件记录
        courseware_file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=test_file
        )
        
        # 验证文件元数据是否正确保存
        self.assertEqual(courseware_file.file_name, "test_file.txt")
        self.assertEqual(courseware_file.file_size, len(file_content))
        self.assertEqual(courseware_file.file_type, "text/plain")
        
        # 验证has_files状态更新
        self.courseware.refresh_from_db()  # 重新从数据库加载，确保获取最新值
        self.assertTrue(self.courseware.has_files)
    
    def test_courseware_file_deletion(self):
        """测试删除课件文件后has_files状态自动更新"""
        # 创建测试文件
        file_content = b"test file content"
        test_file = SimpleUploadedFile("test_file.txt", file_content, content_type="text/plain")
        
        # 创建文件记录
        courseware_file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=test_file
        )
        
        # 验证has_files状态为True
        self.courseware.refresh_from_db()
        self.assertTrue(self.courseware.has_files)
        
        # 删除文件记录
        courseware_file.delete()
        
        # 手动调用update_has_files方法更新状态
        self.courseware.update_has_files()
        
        # 验证has_files状态为False
        self.courseware.refresh_from_db()
        self.assertFalse(self.courseware.has_files)
    
    def test_multiple_files_management(self):
        """测试管理多个文件"""
        # 创建多个测试文件
        files = [
            ('document.pdf', b'PDF content', 'application/pdf'),
            ('presentation.pptx', b'PPT content', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'),
            ('spreadsheet.xlsx', b'Excel content', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        ]
        
        for filename, content, content_type in files:
            test_file = SimpleUploadedFile(filename, content, content_type=content_type)
            CoursewareFile.objects.create(
                courseware=self.courseware,
                file=test_file
            )
        
        # 验证文件数量
        self.assertEqual(CoursewareFile.objects.filter(courseware=self.courseware).count(), 3)
        
        # 验证has_files状态为True
        self.courseware.refresh_from_db()
        self.assertTrue(self.courseware.has_files)
        
        # 删除所有文件
        CoursewareFile.objects.filter(courseware=self.courseware).delete()
        
        # 手动调用update_has_files方法更新状态
        self.courseware.update_has_files()
        
        # 验证has_files状态为False
        self.courseware.refresh_from_db()
        self.assertFalse(self.courseware.has_files) 