from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Course, KnowledgePoint, Courseware

User = get_user_model()

class CourseModelTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password',
            role='teacher'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='科学',
            grade_level='高中',
            teacher=self.user
        )
    
    def test_course_creation(self):
        """测试课程创建"""
        self.assertEqual(self.course.title, '测试课程')
        self.assertEqual(self.course.subject, '科学')
        self.assertEqual(self.course.teacher, self.user)
        self.assertIsNotNone(self.course.created_at)
    
    def test_course_str(self):
        """测试课程字符串表示"""
        self.assertEqual(str(self.course), '测试课程')


class KnowledgePointModelTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password',
            role='teacher'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='科学',
            grade_level='高中',
            teacher=self.user
        )
        
        # 创建父知识点
        self.parent_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='父知识点',
            content='父知识点内容',
            importance=8,
            parent=None
        )
        
        # 创建子知识点
        self.child_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='子知识点',
            content='子知识点内容',
            importance=5,
            parent=self.parent_kp
        )
    
    def test_knowledge_point_creation(self):
        """测试知识点创建"""
        self.assertEqual(self.parent_kp.title, '父知识点')
        self.assertEqual(self.parent_kp.importance, 8)
        self.assertIsNone(self.parent_kp.parent)
        
        self.assertEqual(self.child_kp.title, '子知识点')
        self.assertEqual(self.child_kp.parent, self.parent_kp)
    
    def test_knowledge_point_relationship(self):
        """测试知识点层次关系"""
        # 测试父子关系
        children = self.parent_kp.children.all()
        self.assertEqual(children.count(), 1)
        self.assertEqual(children.first(), self.child_kp)
    
    def test_knowledge_point_str(self):
        """测试知识点字符串表示"""
        self.assertEqual(str(self.parent_kp), '父知识点')
        self.assertEqual(str(self.child_kp), '子知识点')


class CoursewareModelTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password',
            role='teacher'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='科学',
            grade_level='高中',
            teacher=self.user
        )
        
        # 创建测试课件
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='测试课件',
            content='测试课件内容',
            type='document',
            created_by=self.user
        )
    
    def test_courseware_creation(self):
        """测试课件创建"""
        self.assertEqual(self.courseware.title, '测试课件')
        self.assertEqual(self.courseware.type, 'document')
        self.assertEqual(self.courseware.created_by, self.user)
        self.assertEqual(self.courseware.course, self.course)
    
    def test_courseware_str(self):
        """测试课件字符串表示"""
        self.assertEqual(str(self.courseware), '测试课件')
