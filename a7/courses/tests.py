from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from .models import Course, KnowledgePoint, Courseware, Exercise, StudentAnswer

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

class ExerciseModelTests(TestCase):
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
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='测试知识点',
            content='测试知识点内容',
            importance=7,
            parent=None
        )
        
        # 创建测试练习题
        self.exercise = Exercise.objects.create(
            title='测试练习题',
            content='这是一道测试题目的内容',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template='A. 选项1\nB. 选项2\nC. 选项3\nD. 选项4'
        )
    
    def test_exercise_creation(self):
        """测试练习题创建"""
        self.assertEqual(self.exercise.title, '测试练习题')
        self.assertEqual(self.exercise.type, 'single_choice')
        self.assertEqual(self.exercise.difficulty, 3)
        self.assertEqual(self.exercise.knowledge_point, self.knowledge_point)
        self.assertIn('选项1', self.exercise.answer_template)
        self.assertIsNotNone(self.exercise.created_at)
    
    def test_exercise_relationship(self):
        """测试练习题与知识点的关系"""
        exercises = self.knowledge_point.exercises.all()
        self.assertEqual(exercises.count(), 1)
        self.assertEqual(exercises.first(), self.exercise)
    
    def test_exercise_str(self):
        """测试练习题字符串表示"""
        self.assertEqual(str(self.exercise), '测试练习题')

class StudentAnswerModelTests(TestCase):
    def setUp(self):
        # 创建测试教师
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='password',
            role='teacher'
        )
        
        # 创建测试学生
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='password',
            role='student'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='科学',
            grade_level='高中',
            teacher=self.teacher
        )
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='测试知识点',
            content='测试知识点内容',
            importance=7,
            parent=None
        )
        
        # 创建测试练习题
        self.exercise = Exercise.objects.create(
            title='测试练习题',
            content='这是一道测试题目的内容',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template='A. 选项1\nB. 选项2\nC. 选项3\nD. 选项4'
        )
        
        # 创建测试学生答案
        self.student_answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise,
            content='B',
            score=85.0,
            feedback='回答正确，但可以更详细'
        )
    
    def test_student_answer_creation(self):
        """测试学生答案创建"""
        self.assertEqual(self.student_answer.student, self.student)
        self.assertEqual(self.student_answer.exercise, self.exercise)
        self.assertEqual(self.student_answer.content, 'B')
        self.assertEqual(self.student_answer.score, 85.0)
        self.assertEqual(self.student_answer.feedback, '回答正确，但可以更详细')
        self.assertIsNotNone(self.student_answer.submitted_at)
    
    def test_student_answer_relationship(self):
        """测试学生答案与练习题和学生的关系"""
        student_answers = self.exercise.student_answers.all()
        self.assertEqual(student_answers.count(), 1)
        self.assertEqual(student_answers.first(), self.student_answer)
        
        student_answers = self.student.answers.all()
        self.assertEqual(student_answers.count(), 1)
        self.assertEqual(student_answers.first(), self.student_answer)
    
    def test_student_answer_str(self):
        """测试学生答案字符串表示"""
        self.assertEqual(str(self.student_answer), "teststudent - 测试练习题")
    
    def test_unique_together_constraint(self):
        """测试学生对每道题只能有一个答案的约束"""
        # 尝试为同一学生和练习题创建第二个答案，应该引发IntegrityError
        with self.assertRaises(IntegrityError):
            StudentAnswer.objects.create(
                student=self.student,
                exercise=self.exercise,
                content='C',
                score=60.0,
                feedback='答案不正确'
            )
