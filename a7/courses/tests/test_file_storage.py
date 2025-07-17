import os
import uuid
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from courses.models import Course, Courseware, CoursewareFile
from courses.storage import CoursewareFileStorage
from courses.utils import validate_file_type, validate_file_size
from users.models import User, Role

class FileStorageTest(TestCase):
    """测试文件存储功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户和角色
        self.teacher_role = Role.objects.create(name='teacher')
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password123'
        )
        # 设置用户角色
        self.teacher.role = 'teacher'
        self.teacher.role_obj = self.teacher_role
        self.teacher.save()
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='用于测试文件存储功能',
            subject='计算机科学',
            grade_level='大学',
            teacher=self.teacher
        )
        
        # 创建测试课件
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='测试课件',
            content='测试课件内容',
            type='document',
            created_by=self.teacher
        )
        
        # 创建测试文件
        self.test_file_content = b'This is a test file content'
        self.test_file = SimpleUploadedFile(
            name='test_file.pdf',
            content=self.test_file_content,
            content_type='application/pdf'
        )
    
    def test_file_upload(self):
        """测试文件上传功能"""
        # 创建文件记录
        courseware_file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=self.test_file
        )
        
        # 验证文件是否成功保存
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, courseware_file.file.name)))
        self.assertEqual(courseware_file.file_name, 'test_file.pdf')
        self.assertEqual(courseware_file.file_type, 'application/pdf')
        self.assertEqual(courseware_file.file_size, len(self.test_file_content))
        
        # 验证课件的has_files字段是否更新
        self.courseware.refresh_from_db()
        self.assertTrue(self.courseware.has_files)
    
    def test_file_name_uniqueness(self):
        """测试文件名唯一性"""
        # 创建两个同名文件
        file1 = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=SimpleUploadedFile('same_name.pdf', b'content1', content_type='application/pdf')
        )
        
        file2 = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=SimpleUploadedFile('same_name.pdf', b'content2', content_type='application/pdf')
        )
        
        # 验证文件名是否不同
        self.assertNotEqual(file1.file.name, file2.file.name)
    
    def test_file_organization(self):
        """测试文件组织结构"""
        # 上传不同类型的文件
        pdf_file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=SimpleUploadedFile('test.pdf', b'pdf content', content_type='application/pdf')
        )
        
        doc_file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=SimpleUploadedFile('test.docx', b'doc content', 
                                   content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        )
        
        # 验证文件路径是否包含课程ID
        self.assertIn(f'coursewares/{self.course.id}/', pdf_file.file.name)
        self.assertIn(f'coursewares/{self.course.id}/', doc_file.file.name)
        
        # 验证文件是否按类型组织
        self.assertIn('/pdfs/', pdf_file.file.name)
        self.assertIn('/documents/', doc_file.file.name)
    
    def test_file_validation(self):
        """测试文件验证功能"""
        # 测试有效文件类型
        valid_file = SimpleUploadedFile('test.pdf', b'content', content_type='application/pdf')
        self.assertTrue(validate_file_type(valid_file))
        
        # 测试无效文件类型
        invalid_file = SimpleUploadedFile('test.exe', b'content', content_type='application/x-msdownload')
        self.assertFalse(validate_file_type(invalid_file))
        
        # 测试文件大小验证
        small_file = SimpleUploadedFile('small.pdf', b'small content', content_type='application/pdf')
        self.assertTrue(validate_file_size(small_file, max_size_mb=1))
        
        # 创建大文件进行测试
        large_content = b'x' * (2 * 1024 * 1024)  # 2MB
        large_file = SimpleUploadedFile('large.pdf', large_content, content_type='application/pdf')
        self.assertFalse(validate_file_size(large_file, max_size_mb=1))
        self.assertTrue(validate_file_size(large_file, max_size_mb=5))
    
    def test_file_url(self):
        """测试文件URL生成"""
        file = CoursewareFile.objects.create(
            courseware=self.courseware,
            file=self.test_file
        )
        
        # 验证URL是否正确
        expected_url_prefix = settings.MEDIA_URL
        self.assertTrue(file.get_file_url().startswith(expected_url_prefix))
    
    def tearDown(self):
        """清理测试环境"""
        # 删除上传的测试文件
        for courseware_file in CoursewareFile.objects.all():
            if courseware_file.file and os.path.exists(os.path.join(settings.MEDIA_ROOT, courseware_file.file.name)):
                os.remove(os.path.join(settings.MEDIA_ROOT, courseware_file.file.name)) 