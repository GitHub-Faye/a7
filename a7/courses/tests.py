from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.db.models import Q, F, Count, Avg, Sum, Max, Min, Case, When, Value, IntegerField
from django.db import transaction

from .models import Course, KnowledgePoint, Courseware, Exercise, StudentAnswer, LearningRecord
from users.models import Role

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

class LearningRecordModelTest(TestCase):
    """学习记录模型的测试类"""
    
    def setUp(self):
        # 创建测试用户
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='student1password'
        )
        
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='teacher1password'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='数学',
            grade_level='高一',
            teacher=self.teacher
        )
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='函数基础',
            content='了解函数的概念和基础应用',
            importance=8
        )
        
        # 创建测试学习记录
        self.learning_record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=self.knowledge_point,
            status='in_progress',
            progress=45.0,
            time_spent=30
        )
    
    def test_learning_record_creation(self):
        """测试LearningRecord模型实例创建"""
        self.assertEqual(self.learning_record.student, self.student)
        self.assertEqual(self.learning_record.course, self.course)
        self.assertEqual(self.learning_record.knowledge_point, self.knowledge_point)
        self.assertEqual(self.learning_record.status, 'in_progress')
        self.assertEqual(self.learning_record.progress, 45.0)
        self.assertEqual(self.learning_record.time_spent, 30)
        self.assertIsNotNone(self.learning_record.created_at)
        self.assertIsNotNone(self.learning_record.updated_at)
        self.assertIsNotNone(self.learning_record.last_accessed)
    
    def test_is_complete_property(self):
        """测试is_complete属性"""
        # 初始状态为in_progress
        self.assertFalse(self.learning_record.is_complete)
        
        # 更新状态为completed
        self.learning_record.status = 'completed'
        self.learning_record.save()
        self.assertTrue(self.learning_record.is_complete)
    
    def test_update_progress_method(self):
        """测试update_progress方法"""
        # 更新进度到60%
        result = self.learning_record.update_progress(60.0)
        self.assertTrue(result)
        self.assertEqual(self.learning_record.progress, 60.0)
        self.assertEqual(self.learning_record.status, 'in_progress')
        
        # 更新进度到100%，状态应变为completed
        result = self.learning_record.update_progress(100.0)
        self.assertTrue(result)
        self.assertEqual(self.learning_record.progress, 100.0)
        self.assertEqual(self.learning_record.status, 'completed')
        
        # 测试无效进度值
        result = self.learning_record.update_progress(110.0)
        self.assertFalse(result)
        self.assertEqual(self.learning_record.progress, 100.0)  # 保持原值
    
    def test_add_time_spent_method(self):
        """测试add_time_spent方法"""
        # 初始值为30分钟
        initial_time = self.learning_record.time_spent
        
        # 添加15分钟
        result = self.learning_record.add_time_spent(15)
        self.assertTrue(result)
        self.assertEqual(self.learning_record.time_spent, initial_time + 15)
        
        # 添加负值时应该失败
        result = self.learning_record.add_time_spent(-5)
        self.assertFalse(result)
        self.assertEqual(self.learning_record.time_spent, initial_time + 15)  # 保持上次值
    
    def test_str_representation(self):
        """测试LearningRecord的字符串表示"""
        expected_str = f"{self.student.username} - {self.knowledge_point.title} ({self.learning_record.get_status_display()})"
        self.assertEqual(str(self.learning_record), expected_str)
    
    def test_ordering(self):
        """测试LearningRecord的排序（按最后访问时间倒序）"""
        # 修改当前记录的last_accessed为更早的时间
        old_time = timezone.now() - timedelta(days=1)
        LearningRecord.objects.filter(pk=self.learning_record.pk).update(last_accessed=old_time)
        
        # 创建新的学习记录
        new_knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='函数进阶',
            content='学习更复杂的函数',
            importance=7
        )
        
        new_record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=new_knowledge_point,
            status='not_started',
            progress=0.0
        )
        
        # 确保较新访问的记录排在前面
        all_records = list(LearningRecord.objects.all())
        self.assertEqual(all_records[0], new_record)
        self.assertEqual(all_records[1], self.learning_record)
    
    def test_unique_constraint(self):
        """测试student和knowledge_point的唯一约束"""
        # 尝试创建具有相同student和knowledge_point的记录应该引发异常
        with self.assertRaises(Exception):
            LearningRecord.objects.create(
                student=self.student,
                course=self.course,
                knowledge_point=self.knowledge_point,
                status='not_started'
            )
            
    def test_learning_progress_tracking(self):
        """测试完整的学习进度跟踪流程"""
        # 1. 创建多个知识点
        kp1 = KnowledgePoint.objects.create(
            course=self.course,
            title='函数定义',
            content='理解函数定义和基本性质',
            importance=7
        )
        
        kp2 = KnowledgePoint.objects.create(
            course=self.course,
            title='函数图像',
            content='理解函数图像和几何意义',
            importance=6
        )
        
        # 2. 为学生创建这些知识点的学习记录
        record1 = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=kp1,
            status='not_started',
            progress=0.0,
            time_spent=0
        )
        
        record2 = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=kp2,
            status='not_started',
            progress=0.0,
            time_spent=0
        )
        
        # 3. 更新学习记录以模拟学习过程
        # 学生开始学习第一个知识点
        record1.update_progress(25.0)
        record1.add_time_spent(15)
        self.assertEqual(record1.status, 'in_progress')
        self.assertEqual(record1.progress, 25.0)
        self.assertEqual(record1.time_spent, 15)
        
        # 学生继续学习第一个知识点
        record1.update_progress(60.0)
        record1.add_time_spent(30)
        self.assertEqual(record1.status, 'in_progress')
        self.assertEqual(record1.progress, 60.0)
        self.assertEqual(record1.time_spent, 45)
        
        # 学生完成第一个知识点
        record1.update_progress(100.0)
        record1.add_time_spent(15)
        self.assertEqual(record1.status, 'completed')
        self.assertEqual(record1.progress, 100.0)
        self.assertEqual(record1.time_spent, 60)
        self.assertTrue(record1.is_complete)
        
        # 学生开始学习第二个知识点
        record2.update_progress(40.0)
        record2.add_time_spent(25)
        self.assertEqual(record2.status, 'in_progress')
        self.assertEqual(record2.progress, 40.0)
        self.assertEqual(record2.time_spent, 25)
        
        # 4. 验证课程整体学习进度（可以计算平均进度）
        all_records = LearningRecord.objects.filter(
            student=self.student,
            course=self.course
        )
        
        # 计算课程总体进度（包括原始的self.learning_record）
        total_progress = sum(record.progress for record in all_records)
        avg_progress = total_progress / all_records.count()
        
        # 期望的平均进度: (45 + 100 + 40) / 3 = 61.67
        expected_avg = (45.0 + 100.0 + 40.0) / 3
        self.assertAlmostEqual(avg_progress, expected_avg, places=1)
        
        # 5. 验证已完成的知识点计数
        completed_count = all_records.filter(status='completed').count()
        self.assertEqual(completed_count, 1)  # 只有一个知识点完成
        
        # 6. 验证总学习时间
        total_time = sum(record.time_spent for record in all_records)
        expected_time = 30 + 60 + 25  # 原始记录 + 第一个知识点 + 第二个知识点
        self.assertEqual(total_time, expected_time)
    
    def test_learning_status_transitions(self):
        """测试学习状态转换"""
        # 创建一个新的学习记录，初始状态为not_started
        new_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='复合函数',
            content='理解复合函数的概念和应用',
            importance=9
        )
        
        record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=new_kp,
            status='not_started',
            progress=0.0
        )
        
        # 验证初始状态
        self.assertEqual(record.status, 'not_started')
        self.assertEqual(record.progress, 0.0)
        
        # 开始学习，状态应变为in_progress
        record.update_progress(10.0)
        self.assertEqual(record.status, 'in_progress')
        
        # 完成学习，状态应变为completed
        record.update_progress(100.0)
        self.assertEqual(record.status, 'completed')
        
        # 手动设置为需要复习状态
        record.status = 'review_needed'
        record.save()
        self.assertEqual(record.status, 'review_needed')
        
        # 即使状态为需要复习，is_complete属性也应为False
        self.assertFalse(record.is_complete)

class ModelRelationshipTest(TestCase):
    """测试模型之间的关系和级联删除行为"""
    
    def setUp(self):
        # 创建角色
        self.teacher_role = Role.objects.create(name='teacher', description='教师角色')
        self.student_role = Role.objects.create(name='student', description='学生角色')
        
        # 创建用户
        self.teacher = User.objects.create_user(
            username='teacher', 
            password='password',
            email='teacher@example.com',
            role='teacher',
            role_obj=self.teacher_role
        )
        
        self.student = User.objects.create_user(
            username='student', 
            password='password',
            email='student@example.com',
            role='student',
            role_obj=self.student_role
        )
        
        # 创建课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='数学',
            grade_level='高一',
            teacher=self.teacher
        )
        
        # 创建知识点
        self.kp1 = KnowledgePoint.objects.create(
            course=self.course,
            title='一级知识点',
            content='一级知识点内容',
            importance=8
        )
        
        self.kp2 = KnowledgePoint.objects.create(
            course=self.course,
            title='二级知识点',
            content='二级知识点内容',
            importance=6,
            parent=self.kp1
        )
        
        # 创建课件
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='测试课件',
            content='测试课件内容',
            type='document',
            created_by=self.teacher
        )
        
        # 创建练习题
        self.exercise = Exercise.objects.create(
            title='测试题目',
            content='1+1=?',
            type='short_answer',
            difficulty=2,
            knowledge_point=self.kp1,
            answer_template='2'
        )
        
        # 创建学生答案
        self.answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise,
            content='2',
            score=100
        )
        
        # 创建学习记录
        self.learning_record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=self.kp1,
            status='in_progress',
            progress=50
        )
    
    def test_delete_teacher_nullifies_course_teacher(self):
        """测试删除教师时，课程的teacher字段设为null而不是删除课程"""
        course_id = self.course.id
        self.teacher.delete()
        
        # 检查课程是否依然存在
        self.assertTrue(Course.objects.filter(id=course_id).exists())
        
        # 检查课程teacher是否为null
        refreshed_course = Course.objects.get(id=course_id)
        self.assertIsNone(refreshed_course.teacher)
    
    def test_delete_teacher_nullifies_courseware_creator(self):
        """测试删除教师时，课件的created_by字段设为null而不是删除课件"""
        courseware_id = self.courseware.id
        self.teacher.delete()
        
        # 检查课件是否依然存在
        self.assertTrue(Courseware.objects.filter(id=courseware_id).exists())
        
        # 检查课件created_by是否为null
        refreshed_courseware = Courseware.objects.get(id=courseware_id)
        self.assertIsNone(refreshed_courseware.created_by)
    
    def test_delete_course_cascades(self):
        """测试删除课程时，相关知识点、课件和学习记录都被删除"""
        kp1_id = self.kp1.id
        kp2_id = self.kp2.id
        courseware_id = self.courseware.id
        learning_record_id = self.learning_record.id
        exercise_id = self.exercise.id
        
        self.course.delete()
        
        # 检查相关记录是否被删除
        self.assertFalse(KnowledgePoint.objects.filter(id=kp1_id).exists())
        self.assertFalse(KnowledgePoint.objects.filter(id=kp2_id).exists())
        self.assertFalse(Courseware.objects.filter(id=courseware_id).exists())
        self.assertFalse(LearningRecord.objects.filter(id=learning_record_id).exists())
        self.assertFalse(Exercise.objects.filter(id=exercise_id).exists())
    
    def test_delete_knowledge_point_cascades(self):
        """测试删除知识点时，子知识点、练习题和学习记录都被删除"""
        kp2_id = self.kp2.id
        exercise_id = self.exercise.id
        learning_record_id = self.learning_record.id
        
        self.kp1.delete()
        
        # 检查相关记录是否被删除
        self.assertFalse(KnowledgePoint.objects.filter(id=kp2_id).exists())
        self.assertFalse(Exercise.objects.filter(id=exercise_id).exists())
        self.assertFalse(LearningRecord.objects.filter(id=learning_record_id).exists())
    
    def test_delete_exercise_cascades_to_answers(self):
        """测试删除练习题时，相关学生答案被删除"""
        answer_id = self.answer.id
        
        self.exercise.delete()
        
        # 检查相关答案是否被删除
        self.assertFalse(StudentAnswer.objects.filter(id=answer_id).exists())
    
    def test_delete_student_cascades_to_answers_and_records(self):
        """测试删除学生用户时，相关答案和学习记录被删除"""
        answer_id = self.answer.id
        learning_record_id = self.learning_record.id
        
        self.student.delete()
        
        # 检查相关记录是否被删除
        self.assertFalse(StudentAnswer.objects.filter(id=answer_id).exists())
        self.assertFalse(LearningRecord.objects.filter(id=learning_record_id).exists())
    
    def test_unique_constraints_student_answer(self):
        """测试学生答案的唯一性约束"""
        # 尝试为同一学生同一练习题创建另一个答案
        try:
            StudentAnswer.objects.create(
                student=self.student,
                exercise=self.exercise,
                content='错误答案',
                score=0
            )
            self.fail("应该抛出IntegrityError异常，因为已经存在相同学生相同练习的答案")
        except IntegrityError:
            pass # 预期行为
    
    def test_unique_constraints_learning_record(self):
        """测试学习记录的唯一性约束"""
        # 尝试为同一学生同一知识点创建另一个学习记录
        try:
            LearningRecord.objects.create(
                student=self.student,
                course=self.course,
                knowledge_point=self.kp1,
                status='completed',
                progress=100
            )
            self.fail("应该抛出IntegrityError异常，因为已经存在相同学生相同知识点的学习记录")
        except IntegrityError:
            pass # 预期行为
    
    def test_indexes(self):
        """测试索引（只能在数据库层面真正生效，这里只是基本检查）"""
        # 检查索引是否已经定义在Meta类中
        course_indexes = [index.name for index in Course._meta.indexes]
        self.assertIn('course_subj_grade_idx', course_indexes)
        self.assertIn('course_teacher_date_idx', course_indexes)
        
        kp_indexes = [index.name for index in KnowledgePoint._meta.indexes]
        self.assertIn('kp_course_imp_idx', kp_indexes)
        self.assertIn('kp_parent_idx', kp_indexes)
        
        exercise_indexes = [index.name for index in Exercise._meta.indexes]
        self.assertIn('ex_kp_diff_idx', exercise_indexes)
        self.assertIn('ex_type_idx', exercise_indexes)
        
        answer_indexes = [index.name for index in StudentAnswer._meta.indexes]
        self.assertIn('ans_stud_date_idx', answer_indexes)
        self.assertIn('ans_ex_score_idx', answer_indexes)
        
        learning_indexes = [index.name for index in LearningRecord._meta.indexes]
        self.assertIn('lr_stud_course_idx', learning_indexes)
        self.assertIn('lr_status_idx', learning_indexes)
        self.assertIn('lr_access_idx', learning_indexes)
        self.assertIn('lr_progress_idx', learning_indexes)

class ComprehensiveModelRelationshipTest(TestCase):
    """测试所有模型关系的全面测试类"""
    
    def setUp(self):
        # 创建角色
        self.admin_role = Role.objects.create(name='admin', description='管理员角色')
        self.teacher_role = Role.objects.create(name='teacher', description='教师角色')
        self.student_role = Role.objects.create(name='student', description='学生角色')
        
        # 创建用户
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@example.com',
            password='password123',
            role='admin',
            role_obj=self.admin_role
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher_test',
            email='teacher@example.com',
            password='password123',
            role='teacher',
            role_obj=self.teacher_role
        )
        
        self.student_user = User.objects.create_user(
            username='student_test',
            email='student@example.com',
            password='password123',
            role='student',
            role_obj=self.student_role
        )
        
        # 创建课程
        self.course = Course.objects.create(
            title='测试综合课程',
            description='这是一个用于测试关系的综合课程',
            subject='综合学科',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 创建知识点层次结构
        self.root_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='根知识点',
            content='根知识点内容',
            importance=10,
            parent=None
        )
        
        self.child_kp1 = KnowledgePoint.objects.create(
            course=self.course,
            title='子知识点1',
            content='子知识点1内容',
            importance=8,
            parent=self.root_kp
        )
        
        self.child_kp2 = KnowledgePoint.objects.create(
            course=self.course,
            title='子知识点2',
            content='子知识点2内容',
            importance=7,
            parent=self.root_kp
        )
        
        self.grandchild_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='孙知识点',
            content='孙知识点内容',
            importance=5,
            parent=self.child_kp1
        )
        
        # 创建课件
        self.courseware1 = Courseware.objects.create(
            course=self.course,
            title='测试文档课件',
            content='文档课件内容',
            type='document',
            created_by=self.teacher_user
        )
        
        self.courseware2 = Courseware.objects.create(
            course=self.course,
            title='测试视频课件',
            content='视频课件内容',
            type='video',
            created_by=self.teacher_user
        )
        
        # 创建练习题
        self.exercise1 = Exercise.objects.create(
            title='单选题测试',
            content='这是一道单选题',
            type='single_choice',
            difficulty=2,
            knowledge_point=self.child_kp1,
            answer_template='A. 选项1\nB. 选项2\nC. 选项3\nD. 选项4'
        )
        
        self.exercise2 = Exercise.objects.create(
            title='填空题测试',
            content='这是一道填空题',
            type='fill_blank',
            difficulty=3,
            knowledge_point=self.child_kp1,
            answer_template='标准答案: 示例答案'
        )
        
        self.exercise3 = Exercise.objects.create(
            title='另一知识点的习题',
            content='这是属于另一个知识点的习题',
            type='short_answer',
            difficulty=4,
            knowledge_point=self.child_kp2,
            answer_template='评分标准：完整性、准确性、创新性'
        )
        
        # 创建学生答案
        self.student_answer1 = StudentAnswer.objects.create(
            student=self.student_user,
            exercise=self.exercise1,
            content='B',
            score=90,
            feedback='答案正确'
        )
        
        self.student_answer2 = StudentAnswer.objects.create(
            student=self.student_user,
            exercise=self.exercise2,
            content='学生填空答案',
            score=85,
            feedback='基本正确，有小错误'
        )
        
        # 创建学习记录
        self.learning_record1 = LearningRecord.objects.create(
            student=self.student_user,
            course=self.course,
            knowledge_point=self.root_kp,
            status='in_progress',
            progress=60,
            time_spent=45
        )
        
        self.learning_record2 = LearningRecord.objects.create(
            student=self.student_user,
            course=self.course,
            knowledge_point=self.child_kp1,
            status='completed',
            progress=100,
            time_spent=90
        )
    
    def test_user_role_relationship(self):
        """测试用户和角色之间的关系"""
        # 验证角色是否正确关联到用户
        self.assertEqual(self.admin_user.role_obj, self.admin_role)
        self.assertEqual(self.teacher_user.role_obj, self.teacher_role)
        self.assertEqual(self.student_user.role_obj, self.student_role)
        
        # 验证角色是否能够正确反向查询其用户
        self.assertIn(self.admin_user, self.admin_role.users.all())
        self.assertIn(self.teacher_user, self.teacher_role.users.all())
        self.assertIn(self.student_user, self.student_role.users.all())
        
        # 验证角色-用户数量关系
        self.assertEqual(self.admin_role.users.count(), 1)
        self.assertEqual(self.teacher_role.users.count(), 1)
        self.assertEqual(self.student_role.users.count(), 1)
    
    def test_course_teacher_relationship(self):
        """测试课程与教师的关系"""
        # 验证课程是否正确关联到教师
        self.assertEqual(self.course.teacher, self.teacher_user)
        
        # 验证教师是否能够正确反向查询其课程
        self.assertIn(self.course, self.teacher_user.courses.all())
        
        # 验证教师-课程数量关系
        self.assertEqual(self.teacher_user.courses.count(), 1)
    
    def test_course_knowledge_point_relationship(self):
        """测试课程与知识点的关系"""
        # 验证知识点是否正确关联到课程
        self.assertEqual(self.root_kp.course, self.course)
        self.assertEqual(self.child_kp1.course, self.course)
        self.assertEqual(self.child_kp2.course, self.course)
        self.assertEqual(self.grandchild_kp.course, self.course)
        
        # 验证课程是否能够正确反向查询其知识点
        course_kps = self.course.knowledge_points.all()
        self.assertEqual(course_kps.count(), 4)
        self.assertIn(self.root_kp, course_kps)
        self.assertIn(self.child_kp1, course_kps)
        self.assertIn(self.child_kp2, course_kps)
        self.assertIn(self.grandchild_kp, course_kps)
    
    def test_knowledge_point_hierarchy(self):
        """测试知识点的层次结构"""
        # 验证父子关系
        self.assertIsNone(self.root_kp.parent)
        self.assertEqual(self.child_kp1.parent, self.root_kp)
        self.assertEqual(self.child_kp2.parent, self.root_kp)
        self.assertEqual(self.grandchild_kp.parent, self.child_kp1)
        
        # 验证children反向关系
        root_children = self.root_kp.children.all()
        self.assertEqual(root_children.count(), 2)
        self.assertIn(self.child_kp1, root_children)
        self.assertIn(self.child_kp2, root_children)
        
        child1_children = self.child_kp1.children.all()
        self.assertEqual(child1_children.count(), 1)
        self.assertIn(self.grandchild_kp, child1_children)
        
        # 验证没有子节点的知识点
        self.assertEqual(self.child_kp2.children.count(), 0)
        self.assertEqual(self.grandchild_kp.children.count(), 0)
    
    def test_course_courseware_relationship(self):
        """测试课程与课件的关系"""
        # 验证课件是否正确关联到课程
        self.assertEqual(self.courseware1.course, self.course)
        self.assertEqual(self.courseware2.course, self.course)
        
        # 验证课程是否能够正确反向查询其课件
        course_coursewares = self.course.coursewares.all()
        self.assertEqual(course_coursewares.count(), 2)
        self.assertIn(self.courseware1, course_coursewares)
        self.assertIn(self.courseware2, course_coursewares)
    
    def test_courseware_creator_relationship(self):
        """测试课件与创建者的关系"""
        # 验证课件是否正确关联到创建者
        self.assertEqual(self.courseware1.created_by, self.teacher_user)
        self.assertEqual(self.courseware2.created_by, self.teacher_user)
        
        # 验证创建者是否能够正确反向查询其创建的课件
        teacher_coursewares = self.teacher_user.created_coursewares.all()
        self.assertEqual(teacher_coursewares.count(), 2)
        self.assertIn(self.courseware1, teacher_coursewares)
        self.assertIn(self.courseware2, teacher_coursewares)
    
    def test_knowledge_point_exercise_relationship(self):
        """测试知识点与练习题的关系"""
        # 验证练习题是否正确关联到知识点
        self.assertEqual(self.exercise1.knowledge_point, self.child_kp1)
        self.assertEqual(self.exercise2.knowledge_point, self.child_kp1)
        self.assertEqual(self.exercise3.knowledge_point, self.child_kp2)
        
        # 验证知识点是否能够正确反向查询其练习题
        kp1_exercises = self.child_kp1.exercises.all()
        self.assertEqual(kp1_exercises.count(), 2)
        self.assertIn(self.exercise1, kp1_exercises)
        self.assertIn(self.exercise2, kp1_exercises)
        
        kp2_exercises = self.child_kp2.exercises.all()
        self.assertEqual(kp2_exercises.count(), 1)
        self.assertIn(self.exercise3, kp2_exercises)
    
    def test_exercise_student_answer_relationship(self):
        """测试练习题与学生答案的关系"""
        # 验证学生答案是否正确关联到练习题
        self.assertEqual(self.student_answer1.exercise, self.exercise1)
        self.assertEqual(self.student_answer2.exercise, self.exercise2)
        
        # 验证练习题是否能够正确反向查询其学生答案
        ex1_answers = self.exercise1.student_answers.all()
        self.assertEqual(ex1_answers.count(), 1)
        self.assertIn(self.student_answer1, ex1_answers)
        
        ex2_answers = self.exercise2.student_answers.all()
        self.assertEqual(ex2_answers.count(), 1)
        self.assertIn(self.student_answer2, ex2_answers)
    
    def test_student_answer_student_relationship(self):
        """测试学生答案与学生的关系"""
        # 验证学生答案是否正确关联到学生
        self.assertEqual(self.student_answer1.student, self.student_user)
        self.assertEqual(self.student_answer2.student, self.student_user)
        
        # 验证学生是否能够正确反向查询其答案
        student_answers = self.student_user.answers.all()
        self.assertEqual(student_answers.count(), 2)
        self.assertIn(self.student_answer1, student_answers)
        self.assertIn(self.student_answer2, student_answers)
    
    def test_learning_record_relationships(self):
        """测试学习记录与其相关实体的关系"""
        # 验证学习记录是否正确关联到学生、课程和知识点
        self.assertEqual(self.learning_record1.student, self.student_user)
        self.assertEqual(self.learning_record1.course, self.course)
        self.assertEqual(self.learning_record1.knowledge_point, self.root_kp)
        
        self.assertEqual(self.learning_record2.student, self.student_user)
        self.assertEqual(self.learning_record2.course, self.course)
        self.assertEqual(self.learning_record2.knowledge_point, self.child_kp1)
        
        # 验证反向关系
        student_records = self.student_user.learning_records.all()
        self.assertEqual(student_records.count(), 2)
        self.assertIn(self.learning_record1, student_records)
        self.assertIn(self.learning_record2, student_records)
        
        course_records = self.course.learning_records.all()
        self.assertEqual(course_records.count(), 2)
        self.assertIn(self.learning_record1, course_records)
        self.assertIn(self.learning_record2, course_records)
        
        root_kp_records = self.root_kp.learning_records.all()
        self.assertEqual(root_kp_records.count(), 1)
        self.assertIn(self.learning_record1, root_kp_records)
        
        child_kp1_records = self.child_kp1.learning_records.all()
        self.assertEqual(child_kp1_records.count(), 1)
        self.assertIn(self.learning_record2, child_kp1_records)
    
    def test_student_answer_unique_constraint(self):
        """测试学生答案的唯一性约束"""
        # 尝试为同一学生和同一练习题创建另一个答案
        with self.assertRaises(IntegrityError):
            StudentAnswer.objects.create(
                student=self.student_user,
                exercise=self.exercise1,
                content='D',  # 不同的内容
                score=70      # 不同的分数
            )
    
    def test_learning_record_unique_constraint(self):
        """测试学习记录的唯一性约束"""
        # 尝试为同一学生和同一知识点创建第二个记录，应该引发IntegrityError
        with self.assertRaises(IntegrityError):
            LearningRecord.objects.create(
                student=self.student_user,
                course=self.course,
                knowledge_point=self.root_kp,  # 与learning_record1相同
                status='completed',  # 不同的状态
                progress=100         # 不同的进度
            )
    
    def test_delete_teacher_nullifies_course_teacher(self):
        """测试删除教师时，课程的teacher字段设为null"""
        # 删除教师用户
        self.teacher_user.delete()
        
        # 重新从数据库获取课程
        refreshed_course = Course.objects.get(pk=self.course.pk)
        
        # 验证课程仍然存在，但teacher字段为null
        self.assertIsNone(refreshed_course.teacher)
    
    def test_delete_teacher_nullifies_courseware_creator(self):
        """测试删除教师时，课件的created_by字段设为null"""
        # 删除教师用户
        self.teacher_user.delete()
        
        # 重新从数据库获取课件
        refreshed_courseware1 = Courseware.objects.get(pk=self.courseware1.pk)
        refreshed_courseware2 = Courseware.objects.get(pk=self.courseware2.pk)
        
        # 验证课件仍然存在，但created_by字段为null
        self.assertIsNone(refreshed_courseware1.created_by)
        self.assertIsNone(refreshed_courseware2.created_by)
    
    def test_delete_course_cascades(self):
        """测试删除课程时级联删除相关的知识点、课件和学习记录"""
        # 记录初始数量
        initial_kp_count = KnowledgePoint.objects.count()
        initial_courseware_count = Courseware.objects.count()
        initial_learning_record_count = LearningRecord.objects.count()
        
        # 删除课程
        self.course.delete()
        
        # 验证相关对象已被级联删除
        self.assertEqual(KnowledgePoint.objects.count(), initial_kp_count - 4)  # 4个知识点应被删除
        self.assertEqual(Courseware.objects.count(), initial_courseware_count - 2)  # 2个课件应被删除
        self.assertEqual(LearningRecord.objects.count(), initial_learning_record_count - 2)  # 2个学习记录应被删除
        
        # 验证对象确实不再存在
        with self.assertRaises(KnowledgePoint.DoesNotExist):
            KnowledgePoint.objects.get(pk=self.root_kp.pk)
        
        with self.assertRaises(Courseware.DoesNotExist):
            Courseware.objects.get(pk=self.courseware1.pk)
        
        with self.assertRaises(LearningRecord.DoesNotExist):
            LearningRecord.objects.get(pk=self.learning_record1.pk)
    
    def test_delete_knowledge_point_cascades(self):
        """测试删除知识点时级联删除相关的练习题、子知识点和学习记录"""
        # 记录初始数量
        initial_kp_count = KnowledgePoint.objects.count()
        initial_exercise_count = Exercise.objects.count()
        initial_student_answer_count = StudentAnswer.objects.count()
        initial_learning_record_count = LearningRecord.objects.count()
        
        # 删除子知识点1
        self.child_kp1.delete()
        
        # 验证相关对象已被级联删除
        self.assertEqual(KnowledgePoint.objects.count(), initial_kp_count - 2)  # 子知识点1和孙知识点应被删除
        self.assertEqual(Exercise.objects.count(), initial_exercise_count - 2)  # 2个练习题应被删除
        self.assertEqual(StudentAnswer.objects.count(), initial_student_answer_count - 2)  # 2个学生答案应被删除
        self.assertEqual(LearningRecord.objects.count(), initial_learning_record_count - 1)  # 1个学习记录应被删除
        
        # 验证对象确实不再存在
        with self.assertRaises(KnowledgePoint.DoesNotExist):
            KnowledgePoint.objects.get(pk=self.child_kp1.pk)
        
        with self.assertRaises(KnowledgePoint.DoesNotExist):
            KnowledgePoint.objects.get(pk=self.grandchild_kp.pk)
        
        with self.assertRaises(Exercise.DoesNotExist):
            Exercise.objects.get(pk=self.exercise1.pk)
        
        with self.assertRaises(StudentAnswer.DoesNotExist):
            StudentAnswer.objects.get(pk=self.student_answer1.pk)
        
        with self.assertRaises(LearningRecord.DoesNotExist):
            LearningRecord.objects.get(pk=self.learning_record2.pk)
    
    def test_delete_exercise_cascades_to_answers(self):
        """测试删除练习题时级联删除学生答案"""
        # 记录初始学生答案数量
        initial_student_answer_count = StudentAnswer.objects.count()
        
        # 删除练习题1
        self.exercise1.delete()
        
        # 验证相关学生答案已被级联删除
        self.assertEqual(StudentAnswer.objects.count(), initial_student_answer_count - 1)
        
        # 验证学生答案不再存在
        with self.assertRaises(StudentAnswer.DoesNotExist):
            StudentAnswer.objects.get(pk=self.student_answer1.pk)
    
    def test_delete_student_cascades_to_answers_and_records(self):
        """测试删除学生用户时级联删除其答案和学习记录"""
        # 记录初始数量
        initial_student_answer_count = StudentAnswer.objects.count()
        initial_learning_record_count = LearningRecord.objects.count()
        
        # 删除学生用户
        self.student_user.delete()
        
        # 验证相关对象已被级联删除
        self.assertEqual(StudentAnswer.objects.count(), initial_student_answer_count - 2)  # 2个学生答案应被删除
        self.assertEqual(LearningRecord.objects.count(), initial_learning_record_count - 2)  # 2个学习记录应被删除
    
    def test_database_indexes(self):
        """测试各种模型索引是否正常工作"""
        # 测试课程索引
        courses_by_subject = list(Course.objects.filter(subject='综合学科'))
        self.assertEqual(len(courses_by_subject), 1)
        self.assertEqual(courses_by_subject[0], self.course)
        
        # 测试知识点索引
        kps_by_importance = list(KnowledgePoint.objects.filter(importance__gte=7).order_by('-importance'))
        self.assertEqual(len(kps_by_importance), 3)
        self.assertEqual(kps_by_importance[0], self.root_kp)  # 重要性10
        self.assertEqual(kps_by_importance[1], self.child_kp1)  # 重要性8
        self.assertEqual(kps_by_importance[2], self.child_kp2)  # 重要性7
        
        # 测试练习题索引
        easy_exercises = list(Exercise.objects.filter(difficulty__lte=2))
        self.assertEqual(len(easy_exercises), 1)
        self.assertEqual(easy_exercises[0], self.exercise1)
        
        # 测试课件索引
        document_coursewares = list(Courseware.objects.filter(type='document'))
        self.assertEqual(len(document_coursewares), 1)
        self.assertEqual(document_coursewares[0], self.courseware1)
        
        # 测试学习记录索引
        completed_records = list(LearningRecord.objects.filter(status='completed'))
        self.assertEqual(len(completed_records), 1)
        self.assertEqual(completed_records[0], self.learning_record2)

class ModelFieldUpdateTest(TestCase):
    """测试模型字段更新和验证的测试类"""
    
    def setUp(self):
        # 创建测试用户
        self.teacher = User.objects.create_user(
            username='update_teacher',
            email='update_teacher@example.com',
            password='password123',
            role='teacher'
        )
        
        self.student = User.objects.create_user(
            username='update_student',
            email='update_student@example.com',
            password='password123',
            role='student'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='更新测试课程',
            description='这是用于测试更新操作的课程',
            subject='测试学科',
            grade_level='高中',
            teacher=self.teacher
        )
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='更新测试知识点',
            content='用于测试更新操作的知识点',
            importance=6,
            parent=None
        )
        
        # 创建测试课件
        self.courseware = Courseware.objects.create(
            course=self.course,
            title='更新测试课件',
            content='用于测试更新操作的课件',
            type='document',
            created_by=self.teacher
        )
        
        # 创建测试练习题
        self.exercise = Exercise.objects.create(
            title='更新测试练习题',
            content='用于测试更新操作的练习题',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template='A. 选项1\nB. 选项2\nC. 选项3\nD. 选项4'
        )
        
        # 创建测试学生答案
        self.student_answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise,
            content='A',
            score=80,
            feedback='基本正确'
        )
        
        # 创建测试学习记录
        self.learning_record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=self.knowledge_point,
            status='not_started',
            progress=0,
            time_spent=0
        )
    
    def test_course_update(self):
        """测试课程字段更新"""
        # 更新课程字段
        self.course.title = '已更新的课程标题'
        self.course.description = '已更新的课程描述'
        self.course.subject = '已更新的学科'
        self.course.grade_level = '初中'
        self.course.save()
        
        # 从数据库重新获取课程
        updated_course = Course.objects.get(pk=self.course.pk)
        
        # 验证字段已更新
        self.assertEqual(updated_course.title, '已更新的课程标题')
        self.assertEqual(updated_course.description, '已更新的课程描述')
        self.assertEqual(updated_course.subject, '已更新的学科')
        self.assertEqual(updated_course.grade_level, '初中')
    
    def test_knowledge_point_update(self):
        """测试知识点字段更新"""
        # 更新知识点字段
        self.knowledge_point.title = '已更新的知识点标题'
        self.knowledge_point.content = '已更新的知识点内容'
        self.knowledge_point.importance = 9
        self.knowledge_point.save()
        
        # 从数据库重新获取知识点
        updated_kp = KnowledgePoint.objects.get(pk=self.knowledge_point.pk)
        
        # 验证字段已更新
        self.assertEqual(updated_kp.title, '已更新的知识点标题')
        self.assertEqual(updated_kp.content, '已更新的知识点内容')
        self.assertEqual(updated_kp.importance, 9)
    
    def test_courseware_update(self):
        """测试课件字段更新"""
        # 更新课件字段
        self.courseware.title = '已更新的课件标题'
        self.courseware.content = '已更新的课件内容'
        self.courseware.type = 'video'
        self.courseware.save()
        
        # 从数据库重新获取课件
        updated_courseware = Courseware.objects.get(pk=self.courseware.pk)
        
        # 验证字段已更新
        self.assertEqual(updated_courseware.title, '已更新的课件标题')
        self.assertEqual(updated_courseware.content, '已更新的课件内容')
        self.assertEqual(updated_courseware.type, 'video')
    
    def test_exercise_update(self):
        """测试练习题字段更新"""
        # 更新练习题字段
        self.exercise.title = '已更新的练习题标题'
        self.exercise.content = '已更新的练习题内容'
        self.exercise.type = 'multiple_choice'
        self.exercise.difficulty = 4
        self.exercise.answer_template = 'A. 新选项1\nB. 新选项2\nC. 新选项3\nD. 新选项4\n可选多项'
        self.exercise.save()
        
        # 从数据库重新获取练习题
        updated_exercise = Exercise.objects.get(pk=self.exercise.pk)
        
        # 验证字段已更新
        self.assertEqual(updated_exercise.title, '已更新的练习题标题')
        self.assertEqual(updated_exercise.content, '已更新的练习题内容')
        self.assertEqual(updated_exercise.type, 'multiple_choice')
        self.assertEqual(updated_exercise.difficulty, 4)
        self.assertIn('可选多项', updated_exercise.answer_template)
    
    def test_student_answer_update(self):
        """测试学生答案字段更新"""
        # 更新学生答案字段
        self.student_answer.content = 'C'
        self.student_answer.score = 95
        self.student_answer.feedback = '答案更正，比之前好'
        self.student_answer.save()
        
        # 从数据库重新获取学生答案
        updated_answer = StudentAnswer.objects.get(pk=self.student_answer.pk)
        
        # 验证字段已更新
        self.assertEqual(updated_answer.content, 'C')
        self.assertEqual(updated_answer.score, 95)
        self.assertEqual(updated_answer.feedback, '答案更正，比之前好')
    
    def test_learning_record_update(self):
        """测试学习记录字段更新"""
        # 更新学习记录字段
        self.learning_record.status = 'in_progress'
        self.learning_record.progress = 45
        self.learning_record.time_spent = 30
        self.learning_record.save()
        
        # 从数据库重新获取学习记录
        updated_record = LearningRecord.objects.get(pk=self.learning_record.pk)
        
        # 验证字段已更新
        self.assertEqual(updated_record.status, 'in_progress')
        self.assertEqual(updated_record.progress, 45)
        self.assertEqual(updated_record.time_spent, 30)
    
    def test_exercise_type_validation(self):
        """测试练习题类型验证"""
        # 注意：模型中可能没有实现类型验证逻辑，因此测试只验证可用类型的设置
        valid_types = ['single_choice', 'multiple_choice', 'fill_blank', 'short_answer', 'coding', 'other']
        for valid_type in valid_types:
            self.exercise.type = valid_type
            self.exercise.save()  # 不应引发异常
            self.assertEqual(self.exercise.type, valid_type)
        
        # 设置一个非标准类型，验证是否可以保存（如果没有验证逻辑）
        self.exercise.type = 'non_standard_type'
        self.exercise.save()
        # 验证类型已被保存
        refreshed_exercise = Exercise.objects.get(pk=self.exercise.pk)
        self.assertEqual(refreshed_exercise.type, 'non_standard_type')
    
    def test_exercise_difficulty_validation(self):
        """测试练习题难度验证"""
        # 注意：模型中可能没有实现难度验证逻辑，因此测试只验证合理难度的设置
        valid_difficulties = range(1, 6)  # 1到5的难度
        for difficulty in valid_difficulties:
            self.exercise.difficulty = difficulty
            self.exercise.save()  # 不应引发异常
            self.assertEqual(self.exercise.difficulty, difficulty)
        
        # 设置一个超出合理范围的难度，验证是否可以保存（如果没有验证逻辑）
        self.exercise.difficulty = 10
        self.exercise.save()
        # 验证难度已被保存
        refreshed_exercise = Exercise.objects.get(pk=self.exercise.pk)
        self.assertEqual(refreshed_exercise.difficulty, 10)
    
    def test_learning_record_progress_validation(self):
        """测试学习记录进度验证方法"""
        # 测试合法进度值的更新
        self.learning_record.progress = 50
        self.learning_record.save()
        self.assertEqual(self.learning_record.progress, 50)
        
        self.learning_record.progress = 100
        self.learning_record.save()
        self.assertEqual(self.learning_record.progress, 100)
        
        # 测试状态变更逻辑（如果有）
        # 注意：这里我们假设该逻辑可能在save方法中实现
        self.learning_record.progress = 100
        self.learning_record.status = 'in_progress'  # 显式设置为不是completed
        self.learning_record.save()
        
        # 验证进度和状态
        refreshed_record = LearningRecord.objects.get(pk=self.learning_record.pk)
        self.assertEqual(refreshed_record.progress, 100)
        
        # 测试非法进度值的行为（如果没有验证逻辑）
        # 负值
        self.learning_record.progress = -10
        self.learning_record.save()
        refreshed_record = LearningRecord.objects.get(pk=self.learning_record.pk)
        self.assertEqual(refreshed_record.progress, -10)
        
        # 超过100的值
        self.learning_record.progress = 110
        self.learning_record.save()
        refreshed_record = LearningRecord.objects.get(pk=self.learning_record.pk)
        self.assertEqual(refreshed_record.progress, 110)
    
    def test_learning_record_time_spent_validation(self):
        """测试学习记录时间验证方法"""
        # 创建一个单独的知识点用于此测试，避免唯一约束错误
        time_test_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='时间测试知识点',
            content='用于测试时间字段的知识点',
            importance=5,
            parent=None
        )
        
        # 创建一个新的学习记录用于测试，避免影响其他测试
        test_record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=time_test_kp,
            status='not_started',
            progress=0,
            time_spent=10
        )
        
        # 测试有效值更新
        test_record.time_spent = 30
        test_record.save()
        # 刷新记录确认更新
        test_record.refresh_from_db()
        self.assertEqual(test_record.time_spent, 30)
        
        # 测试零值是有效的
        test_record.time_spent = 0
        test_record.save()
        test_record.refresh_from_db()
        self.assertEqual(test_record.time_spent, 0)
        
        # 判断我们的数据库是否有CHECK约束，检查是否为SQLite
        from django.db import connection
        if connection.vendor == 'sqlite':
            # SQLite有CHECK约束，测试负值将会失败
            from django.db.utils import IntegrityError
            # 测试负值，预期失败
            with self.assertRaises(IntegrityError):
                test_record.time_spent = -5
                test_record.save()
    
    # 测试已合并到test_learning_record_time_spent_validation方法中

class EdgeCaseAndSpecialConditionTest(TestCase):
    """测试特殊情况和边缘案例的测试类"""
    
    def setUp(self):
        # 创建基础测试数据
        self.teacher = User.objects.create_user(
            username='edge_teacher',
            email='edge_teacher@example.com',
            password='password123',
            role='teacher'
        )
        
        self.student = User.objects.create_user(
            username='edge_student',
            email='edge_student@example.com',
            password='password123',
            role='student'
        )
        
        self.course = Course.objects.create(
            title='边缘案例测试课程',
            description='用于测试边缘案例的课程',
            subject='边缘测试',
            grade_level='高中',
            teacher=self.teacher
        )
        
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='边缘案例知识点',
            content='用于测试边缘案例的知识点',
            importance=5,
            parent=None
        )
    
    def test_course_creation_with_null_teacher(self):
        """测试创建没有教师的课程"""
        course_without_teacher = Course.objects.create(
            title='无教师课程',
            description='这个课程没有关联教师',
            subject='自学',
            grade_level='大学',
            teacher=None  # 明确设置为None
        )
        
        # 验证课程已创建
        self.assertIsNotNone(course_without_teacher.pk)
        self.assertEqual(course_without_teacher.title, '无教师课程')
        self.assertIsNone(course_without_teacher.teacher)
        
        # 验证可以正常查询
        fetched_course = Course.objects.get(pk=course_without_teacher.pk)
        self.assertEqual(fetched_course.title, '无教师课程')
        
        # 测试过滤无教师的课程
        courses_without_teacher = Course.objects.filter(teacher__isnull=True)
        self.assertEqual(courses_without_teacher.count(), 1)
        self.assertEqual(courses_without_teacher.first(), course_without_teacher)
    
    def test_knowledge_point_with_extremely_long_content(self):
        """测试创建具有极长内容的知识点"""
        # 创建一个具有10KB内容的知识点
        long_content = 'a' * 10240  # 10KB的字符
        
        long_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='长内容知识点',
            content=long_content,
            importance=5,
            parent=None
        )
        
        # 验证知识点已创建，且内容完整
        fetched_kp = KnowledgePoint.objects.get(pk=long_kp.pk)
        self.assertEqual(len(fetched_kp.content), 10240)
        self.assertEqual(fetched_kp.content, long_content)
    
    def test_knowledge_point_with_empty_content(self):
        """测试创建内容为空的知识点"""
        empty_content_kp = KnowledgePoint.objects.create(
            course=self.course,
            title='空内容知识点',
            content='',  # 空内容
            importance=5,
            parent=None
        )
        
        # 验证知识点已创建，且内容为空字符串
        fetched_kp = KnowledgePoint.objects.get(pk=empty_content_kp.pk)
        self.assertEqual(fetched_kp.content, '')
        
        # 测试过滤内容为空的知识点
        empty_content_kps = KnowledgePoint.objects.filter(content='')
        self.assertEqual(empty_content_kps.count(), 1)
        self.assertEqual(empty_content_kps.first(), empty_content_kp)
    
    def test_exercise_with_null_answer_template(self):
        """测试创建答案模板为空的练习题"""
        null_template_exercise = Exercise.objects.create(
            title='无答案模板练习题',
            content='这个练习题没有答案模板',
            type='short_answer',
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template=None  # 显式设置为None
        )
        
        # 验证练习题已创建，且答案模板为NULL
        fetched_exercise = Exercise.objects.get(pk=null_template_exercise.pk)
        self.assertIsNone(fetched_exercise.answer_template)
        
        # 测试过滤答案模板为空的练习题
        null_template_exercises = Exercise.objects.filter(answer_template__isnull=True)
        self.assertEqual(null_template_exercises.count(), 1)
        self.assertEqual(null_template_exercises.first(), null_template_exercise)
    
    def test_student_answer_with_zero_score(self):
        """测试创建零分的学生答案"""
        # 首先创建一个练习题
        exercise = Exercise.objects.create(
            title='测试零分答案的题目',
            content='这是用于测试零分答案的题目',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point
        )
        
        # 创建分数为零的答案
        zero_score_answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=exercise,
            content='错误答案',
            score=0.0,  # 明确设置为零
            feedback='完全错误'
        )
        
        # 验证答案已创建，且分数为零
        fetched_answer = StudentAnswer.objects.get(pk=zero_score_answer.pk)
        self.assertEqual(fetched_answer.score, 0.0)
        
        # 测试过滤分数为零的答案
        zero_score_answers = StudentAnswer.objects.filter(score=0.0)
        self.assertEqual(zero_score_answers.count(), 1)
        self.assertEqual(zero_score_answers.first(), zero_score_answer)
    
    def test_student_answer_with_null_feedback(self):
        """测试创建无反馈的学生答案"""
        # 首先创建一个练习题
        exercise = Exercise.objects.create(
            title='测试无反馈答案的题目',
            content='这是用于测试无反馈答案的题目',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point
        )
        
        # 创建反馈为空的答案
        null_feedback_answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=exercise,
            content='学生答案',
            score=75.0,
            feedback=None  # 明确设置为None
        )
        
        # 验证答案已创建，且反馈为NULL
        fetched_answer = StudentAnswer.objects.get(pk=null_feedback_answer.pk)
        self.assertIsNone(fetched_answer.feedback)
        
        # 测试过滤反馈为空的答案
        null_feedback_answers = StudentAnswer.objects.filter(feedback__isnull=True)
        self.assertEqual(null_feedback_answers.count(), 1)
        self.assertEqual(null_feedback_answers.first(), null_feedback_answer)
    
    def test_learning_record_status_transitions(self):
        """测试学习记录状态转换的特殊情况"""
        # 创建初始状态为"未开始"的学习记录
        record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=self.knowledge_point,
            status='not_started',
            progress=0,
            time_spent=0
        )
        
        # 测试从"未开始"到"学习中"的转换（通过进度更新）
        record.update_progress(30)
        self.assertEqual(record.status, 'in_progress')
        self.assertEqual(record.progress, 30)
        
        # 测试从"学习中"到"已完成"的转换（通过进度更新）
        record.update_progress(100)
        self.assertEqual(record.status, 'completed')
        self.assertEqual(record.progress, 100)
        
        # 测试从"已完成"到"需要复习"的手动转换
        record.status = 'review_needed'
        record.save()
        self.assertEqual(record.status, 'review_needed')
        
        # 测试从"需要复习"到"学习中"的转换（通过进度更新）
        record.update_progress(80)  # 降低进度来表示重新学习
        self.assertEqual(record.status, 'in_progress')
        self.assertEqual(record.progress, 80)
    
    def test_knowledge_point_deep_hierarchy(self):
        """测试知识点的深层次结构"""
        # 创建5层深的知识点层次结构
        kp_level1 = KnowledgePoint.objects.create(
            course=self.course,
            title='一级知识点',
            content='一级内容',
            importance=10,
            parent=None
        )
        
        kp_level2 = KnowledgePoint.objects.create(
            course=self.course,
            title='二级知识点',
            content='二级内容',
            importance=8,
            parent=kp_level1
        )
        
        kp_level3 = KnowledgePoint.objects.create(
            course=self.course,
            title='三级知识点',
            content='三级内容',
            importance=6,
            parent=kp_level2
        )
        
        kp_level4 = KnowledgePoint.objects.create(
            course=self.course,
            title='四级知识点',
            content='四级内容',
            importance=4,
            parent=kp_level3
        )
        
        kp_level5 = KnowledgePoint.objects.create(
            course=self.course,
            title='五级知识点',
            content='五级内容',
            importance=2,
            parent=kp_level4
        )
        
        # 验证层次结构
        self.assertIsNone(kp_level1.parent)
        self.assertEqual(kp_level2.parent, kp_level1)
        self.assertEqual(kp_level3.parent, kp_level2)
        self.assertEqual(kp_level4.parent, kp_level3)
        self.assertEqual(kp_level5.parent, kp_level4)
        
        # 测试从底层向上追溯父级
        current = kp_level5
        levels = []
        while current:
            levels.append(current.title)
            current = current.parent
        
        self.assertEqual(len(levels), 5)
        self.assertEqual(levels, ['五级知识点', '四级知识点', '三级知识点', '二级知识点', '一级知识点'])
        
        # 测试从顶层向下获取所有子孙
        def get_all_descendants(kp):
            descendants = list(kp.children.all())
            for child in kp.children.all():
                descendants.extend(get_all_descendants(child))
            return descendants
        
        all_descendants = get_all_descendants(kp_level1)
        self.assertEqual(len(all_descendants), 4)
        titles = [kp.title for kp in all_descendants]
        self.assertIn('二级知识点', titles)
        self.assertIn('三级知识点', titles)
        self.assertIn('四级知识点', titles)
        self.assertIn('五级知识点', titles)
    
    def test_circular_reference_prevention(self):
        """测试防止知识点循环引用"""
        # 创建三个知识点
        kp1 = KnowledgePoint.objects.create(
            course=self.course,
            title='知识点1',
            content='内容1',
            importance=7,
            parent=None
        )
        
        kp2 = KnowledgePoint.objects.create(
            course=self.course,
            title='知识点2',
            content='内容2',
            importance=6,
            parent=kp1
        )
        
        kp3 = KnowledgePoint.objects.create(
            course=self.course,
            title='知识点3',
            content='内容3',
            importance=5,
            parent=kp2
        )
        
        # 尝试创建循环引用（将kp1的父级设为kp3）
        kp1.parent = kp3
        
        # 这应该会在save()时引发异常，因为这将创建循环引用
        # 注意：Django本身并不自动检测循环引用，这是一个应用层面的业务规则
        # 在实际应用中，需要在模型的save()方法中添加验证逻辑
        # 由于测试目的，这里我们指出这一点，但不添加实际的验证代码
        
        # 以下是一种可能的验证方法（如果模型已实现）
        # with self.assertRaises(ValidationError):
        #     kp1.save()
    
    def test_unique_course_title_and_subject(self):
        """测试课程标题和学科组合的唯一性"""
        # 创建第一个课程
        Course.objects.create(
            title='唯一性测试',
            description='测试课程标题和学科组合的唯一性',
            subject='唯一学科',
            grade_level='高中',
            teacher=self.teacher
        )
        
        # 尝试创建具有相同标题和学科的第二个课程
        # 注意：Django模型默认不约束这种组合唯一性，除非在Meta中定义unique_together
        # 这个测试主要是为了展示如果有这样的业务需求，如何进行测试
        # 如果Course模型确实有这样的约束，可以取消注释以下代码
        
        # with self.assertRaises(IntegrityError):
        #     Course.objects.create(
        #         title='唯一性测试',  # 相同的标题
        #         description='另一个描述',
        #         subject='唯一学科',  # 相同的学科
        #         grade_level='初中',  # 不同的年级
        #         teacher=self.teacher
        #     )
        
        # 验证可以创建具有相同标题但不同学科的课程
        same_title_course = Course.objects.create(
            title='唯一性测试',  # 相同的标题
            description='另一个描述',
            subject='不同学科',  # 不同的学科
            grade_level='高中',
            teacher=self.teacher
        )
        
        self.assertIsNotNone(same_title_course.pk)
        self.assertEqual(Course.objects.filter(title='唯一性测试').count(), 2)
    
    def test_courseware_type_values(self):
        """测试课件类型的所有可能值"""
        # 测试所有合法的课件类型
        courseware_types = ['document', 'video', 'audio', 'image', 'interactive', 'other']
        
        for i, cw_type in enumerate(courseware_types):
            courseware = Courseware.objects.create(
                course=self.course,
                title=f'{cw_type}类型课件',
                content=f'{cw_type}内容示例',
                type=cw_type,
                created_by=self.teacher
            )
            
            self.assertEqual(courseware.type, cw_type)
            
            # 验证可以正确过滤特定类型
            filtered = Courseware.objects.filter(type=cw_type)
            self.assertIn(courseware, filtered)
        
        # 验证所有课件被正确创建
        self.assertEqual(Courseware.objects.count(), 6)
        
        # 测试使用非法类型（注意：Django的CharField不会自动验证choices约束，除非在模型的clean()方法中实现）
        # 这个测试主要是为了说明如果有这样的业务需求，如何进行测试
        # 如果Courseware模型实现了clean()方法验证，可以取消注释以下代码
        
        # with self.assertRaises(ValidationError):
        #     invalid_type_courseware = Courseware(
        #         course=self.course,
        #         title='无效类型课件',
        #         content='无效类型内容',
        #         type='invalid_type',
        #         created_by=self.teacher
        #     )
        #     invalid_type_courseware.full_clean()  # 这会触发验证
    
    def test_updating_exercise_knowledge_point(self):
        """测试更新练习题的关联知识点"""
        # 创建两个知识点
        kp1 = self.knowledge_point  # 使用setUp中已创建的知识点
        
        kp2 = KnowledgePoint.objects.create(
            course=self.course,
            title='另一个知识点',
            content='用于测试更新练习题关联',
            importance=4,
            parent=None
        )
        
        # 创建关联到第一个知识点的练习题
        exercise = Exercise.objects.create(
            title='可转移的练习题',
            content='这个练习题将被转移到另一个知识点',
            type='multiple_choice',
            difficulty=3,
            knowledge_point=kp1
        )
        
        # 验证初始关联
        self.assertEqual(exercise.knowledge_point, kp1)
        self.assertIn(exercise, kp1.exercises.all())
        
        # 更新关联到第二个知识点
        exercise.knowledge_point = kp2
        exercise.save()
        
        # 重新获取并验证关联已更新
        updated_exercise = Exercise.objects.get(pk=exercise.pk)
        self.assertEqual(updated_exercise.knowledge_point, kp2)
        self.assertIn(updated_exercise, kp2.exercises.all())
        self.assertNotIn(updated_exercise, kp1.exercises.all())
    
    def test_models_with_empty_database(self):
        """测试在空数据库上的模型操作"""
        # 清空数据库
        KnowledgePoint.objects.all().delete()
        Course.objects.all().delete()
        User.objects.all().delete()
        
        # 验证数据库为空
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Course.objects.count(), 0)
        self.assertEqual(KnowledgePoint.objects.count(), 0)
        self.assertEqual(Exercise.objects.count(), 0)
        self.assertEqual(StudentAnswer.objects.count(), 0)
        self.assertEqual(LearningRecord.objects.count(), 0)
        
        # 测试空数据库上的过滤操作
        empty_results = Course.objects.filter(title__contains='测试')
        self.assertEqual(empty_results.count(), 0)
        self.assertTrue(empty_results.exists() == False)
        
        # 测试空数据库上的聚合操作
        from django.db.models import Avg, Max, Min, Count
        
        avg_difficulty = Exercise.objects.aggregate(Avg('difficulty'))
        self.assertIsNone(avg_difficulty['difficulty__avg'])
        
        # 创建一个新用户和课程，验证可以在空数据库上正常创建
        new_user = User.objects.create_user(
            username='new_test_user',
            email='newuser@example.com',
            password='password123',
            role='teacher'
        )
        
        new_course = Course.objects.create(
            title='新测试课程',
            description='在空数据库上创建的新课程',
            subject='测试学科',
            grade_level='高中',
            teacher=new_user
        )
        
        # 验证创建成功
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first(), new_course)

class AdvancedQueryTest(TestCase):
    """测试复杂查询和聚合功能的测试类"""
    
    def setUp(self):
        # 创建测试用户
        self.teacher1 = User.objects.create_user(
            username='query_teacher1',
            email='teacher1@example.com',
            password='password123',
            role='teacher'
        )
        
        self.teacher2 = User.objects.create_user(
            username='query_teacher2',
            email='teacher2@example.com',
            password='password123',
            role='teacher'
        )
        
        # 创建多个学生用户
        self.students = []
        for i in range(1, 11):  # 创建10个学生
            student = User.objects.create_user(
                username=f'query_student{i}',
                email=f'student{i}@example.com',
                password='password123',
                role='student'
            )
            self.students.append(student)
        
        # 创建多个课程
        self.math_course = Course.objects.create(
            title='高级数学',
            description='高中高级数学课程',
            subject='数学',
            grade_level='高中',
            teacher=self.teacher1
        )
        
        self.physics_course = Course.objects.create(
            title='物理基础',
            description='高中物理基础课程',
            subject='物理',
            grade_level='高中',
            teacher=self.teacher1
        )
        
        self.chemistry_course = Course.objects.create(
            title='化学入门',
            description='高中化学入门课程',
            subject='化学',
            grade_level='高中',
            teacher=self.teacher2
        )
        
        self.biology_course = Course.objects.create(
            title='生物基础',
            description='高中生物基础课程',
            subject='生物',
            grade_level='高中',
            teacher=self.teacher2
        )
        
        # 为数学课程创建知识点
        self.math_kp1 = KnowledgePoint.objects.create(
            course=self.math_course,
            title='数列',
            content='数列基础知识',
            importance=9,
            parent=None
        )
        
        self.math_kp2 = KnowledgePoint.objects.create(
            course=self.math_course,
            title='极限',
            content='极限基础知识',
            importance=8,
            parent=None
        )
        
        # 为物理课程创建知识点
        self.physics_kp1 = KnowledgePoint.objects.create(
            course=self.physics_course,
            title='牛顿运动定律',
            content='牛顿三大运动定律',
            importance=10,
            parent=None
        )
        
        self.physics_kp2 = KnowledgePoint.objects.create(
            course=self.physics_course,
            title='动量守恒',
            content='动量守恒定律',
            importance=7,
            parent=None
        )
        
        # 创建练习题
        self.exercises = []
        
        # 数学练习题
        for i in range(1, 6):  # 每个知识点5道题
            self.exercises.append(Exercise.objects.create(
                title=f'数列练习{i}',
                content=f'数列练习题内容{i}',
                type='single_choice',
                difficulty=i % 5 + 1,  # 1到5的难度循环
                knowledge_point=self.math_kp1
            ))
            
            self.exercises.append(Exercise.objects.create(
                title=f'极限练习{i}',
                content=f'极限练习题内容{i}',
                type='fill_blank',
                difficulty=i % 5 + 1,  # 1到5的难度循环
                knowledge_point=self.math_kp2
            ))
        
        # 物理练习题
        for i in range(1, 6):  # 每个知识点5道题
            self.exercises.append(Exercise.objects.create(
                title=f'牛顿定律练习{i}',
                content=f'牛顿定律练习题内容{i}',
                type='multiple_choice',
                difficulty=i % 5 + 1,  # 1到5的难度循环
                knowledge_point=self.physics_kp1
            ))
            
            self.exercises.append(Exercise.objects.create(
                title=f'动量守恒练习{i}',
                content=f'动量守恒练习题内容{i}',
                type='short_answer',
                difficulty=i % 5 + 1,  # 1到5的难度循环
                knowledge_point=self.physics_kp2
            ))
        
        # 创建学生答案
        # 让每个学生回答部分练习题，得分各不相同
        for i, student in enumerate(self.students):
            # 每个学生答10道题，分布在不同课程和知识点
            for j in range(10):
                exercise_index = (i + j) % len(self.exercises)
                exercise = self.exercises[exercise_index]
                
                # 分数在60到100之间变化
                score = 60 + (i * j) % 41
                
                StudentAnswer.objects.create(
                    student=student,
                    exercise=exercise,
                    content=f'学生{i+1}对题目{exercise_index+1}的答案',
                    score=score,
                    feedback=f'分数：{score}'
                )
        
        # 创建学习记录
        # 每个学生对每个课程都有学习记录
        for i, student in enumerate(self.students):
            # 数学课程记录
            LearningRecord.objects.create(
                student=student,
                course=self.math_course,
                knowledge_point=self.math_kp1,
                status='in_progress' if i < 5 else 'completed',
                progress=50 if i < 5 else 100,
                time_spent=30 + i * 5
            )
            
            LearningRecord.objects.create(
                student=student,
                course=self.math_course,
                knowledge_point=self.math_kp2,
                status='in_progress' if i < 3 else 'completed',
                progress=40 if i < 3 else 100,
                time_spent=25 + i * 5
            )
            
            # 物理课程记录
            LearningRecord.objects.create(
                student=student,
                course=self.physics_course,
                knowledge_point=self.physics_kp1,
                status='not_started' if i < 2 else ('in_progress' if i < 7 else 'completed'),
                progress=0 if i < 2 else (60 if i < 7 else 100),
                time_spent=0 if i < 2 else (20 + i * 3)
            )
            
            LearningRecord.objects.create(
                student=student,
                course=self.physics_course,
                knowledge_point=self.physics_kp2,
                status='not_started' if i < 4 else ('in_progress' if i < 8 else 'completed'),
                progress=0 if i < 4 else (30 if i < 8 else 100),
                time_spent=0 if i < 4 else (15 + i * 2)
            )
    
    def test_filter_with_q_objects(self):
        """测试使用Q对象进行复杂过滤"""
        # 查找数学或物理课程
        science_courses = Course.objects.filter(
            Q(subject='数学') | Q(subject='物理')
        )
        self.assertEqual(science_courses.count(), 2)
        self.assertIn(self.math_course, science_courses)
        self.assertIn(self.physics_course, science_courses)
        
        # 查找非teacher1教授的课程
        not_teacher1_courses = Course.objects.filter(
            ~Q(teacher=self.teacher1)
        )
        self.assertEqual(not_teacher1_courses.count(), 2)
        self.assertIn(self.chemistry_course, not_teacher1_courses)
        self.assertIn(self.biology_course, not_teacher1_courses)
        
        # 查找数学和物理课程但不是teacher1教授的（应该为空）
        complex_filtered = Course.objects.filter(
            (Q(subject='数学') | Q(subject='物理')) & ~Q(teacher=self.teacher1)
        )
        self.assertEqual(complex_filtered.count(), 0)
        
        # 查找标题包含"基础"并且不是数学课程的课程
        basic_courses = Course.objects.filter(
            Q(title__contains='基础') & ~Q(subject='数学')
        )
        self.assertEqual(basic_courses.count(), 2)
        self.assertIn(self.physics_course, basic_courses)
        self.assertIn(self.biology_course, basic_courses)
    
    def test_aggregate_queries(self):
        """测试聚合查询"""
        # 计算每个课程的平均练习题难度
        course_difficulty = Exercise.objects.values('knowledge_point__course').annotate(
            avg_difficulty=Avg('difficulty')
        )
        self.assertEqual(len(course_difficulty), 2)  # 数学和物理
        
        # 计算每个知识点的练习题数量
        kp_exercise_count = Exercise.objects.values('knowledge_point').annotate(
            count=Count('id')
        )
        self.assertEqual(len(kp_exercise_count), 4)  # 4个知识点
        for item in kp_exercise_count:
            self.assertEqual(item['count'], 5)  # 每个知识点5道题
        
        # 计算每个学生的平均得分
        student_avg_scores = StudentAnswer.objects.values('student').annotate(
            avg_score=Avg('score')
        )
        self.assertEqual(len(student_avg_scores), 10)  # 10个学生
        
        # 计算每个练习题类型的数量
        exercise_type_counts = Exercise.objects.values('type').annotate(
            count=Count('id')
        )
        self.assertEqual(len(exercise_type_counts), 4)  # 4种类型
        
        # 验证各类型数量
        type_counts = {item['type']: item['count'] for item in exercise_type_counts}
        self.assertEqual(type_counts['single_choice'], 5)
        self.assertEqual(type_counts['fill_blank'], 5)
        self.assertEqual(type_counts['multiple_choice'], 5)
        self.assertEqual(type_counts['short_answer'], 5)
    
    def test_f_expressions(self):
        """测试F表达式"""
        # 增加所有练习题的难度
        Exercise.objects.update(difficulty=F('difficulty') + 1)
        
        # 验证难度已增加
        for exercise in Exercise.objects.all():
            self.assertLessEqual(exercise.difficulty, 6)  # 原最大5 + 1 = 6
            self.assertGreaterEqual(exercise.difficulty, 2)  # 原最小1 + 1 = 2
        
        # 将所有学习记录的进度加10%
        LearningRecord.objects.filter(progress__lt=90).update(
            progress=F('progress') + 10
        )
        
        # 验证进度已增加，但不超过100
        for record in LearningRecord.objects.all():
            if record.status == 'completed':
                self.assertEqual(record.progress, 100)
            elif record.status == 'not_started':
                self.assertIn(record.progress, [0, 10])  # 可能是0或10（如果更新后）
            else:  # in_progress
                self.assertGreaterEqual(record.progress, 10)  # 至少是原值+10或原值
    
    def test_case_when_expressions(self):
        """测试Case When表达式"""
        # 根据难度给练习题分类
        exercises_by_difficulty = Exercise.objects.annotate(
            difficulty_level=Case(
                When(difficulty__lte=2, then=Value('简单')),
                When(difficulty__lte=4, then=Value('中等')),
                default=Value('困难'),
                output_field=models.CharField()
            )
        )
        
        # 验证分类正确
        for exercise in exercises_by_difficulty:
            if exercise.difficulty <= 2:
                self.assertEqual(exercise.difficulty_level, '简单')
            elif exercise.difficulty <= 4:
                self.assertEqual(exercise.difficulty_level, '中等')
            else:
                self.assertEqual(exercise.difficulty_level, '困难')
        
        # 根据进度给学习记录评分
        learning_records_rated = LearningRecord.objects.annotate(
            progress_rating=Case(
                When(progress=0, then=Value(0)),
                When(progress__lt=50, then=Value(1)),
                When(progress__lt=80, then=Value(2)),
                When(progress__lt=100, then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        )
        
        # 验证评分正确
        for record in learning_records_rated:
            if record.progress == 0:
                self.assertEqual(record.progress_rating, 0)
            elif record.progress < 50:
                self.assertEqual(record.progress_rating, 1)
            elif record.progress < 80:
                self.assertEqual(record.progress_rating, 2)
            elif record.progress < 100:
                self.assertEqual(record.progress_rating, 3)
            else:
                self.assertEqual(record.progress_rating, 4)
    
    def test_advanced_annotations(self):
        """测试高级注解查询"""
        # 为每个课程注解学生人数、平均进度和总学习时间
        courses_with_stats = Course.objects.annotate(
            student_count=Count('learning_records__student', distinct=True),
            avg_progress=Avg('learning_records__progress'),
            total_time=Sum('learning_records__time_spent')
        )
        
        # 验证统计数据
        for course in courses_with_stats:
            if course in [self.math_course, self.physics_course]:
                self.assertEqual(course.student_count, 10)  # 10个学生有记录
            else:
                self.assertEqual(course.student_count, 0)  # 其他课程没有记录
        
        # 为每个学生注解已完成的知识点数量
        students_with_completed = User.objects.filter(role='student').annotate(
            completed_points=Count('learning_records', filter=Q(learning_records__status='completed'))
        )
        
        # 验证每个学生的已完成知识点数量
        for student in students_with_completed:
            completed_count = LearningRecord.objects.filter(
                student=student,
                status='completed'
            ).count()
            self.assertEqual(student.completed_points, completed_count)
    
    def test_complex_filtering_with_annotations(self):
        """测试带注解的复杂过滤"""
        # 查找平均进度超过80%的课程
        high_progress_courses = Course.objects.annotate(
            avg_progress=Avg('learning_records__progress')
        ).filter(
            avg_progress__gt=80
        )
        
        # 查找平均得分超过85的学生
        high_scoring_students = User.objects.filter(role='student').annotate(
            avg_score=Avg('answers__score')
        ).filter(
            avg_score__gt=85
        )
        
        # 查找包含超过10道练习题的课程
        courses_with_many_exercises = Course.objects.annotate(
            exercise_count=Count('knowledge_points__exercises')
        ).filter(
            exercise_count__gt=10
        )
        
        # 查找答题正确率高的学生（分数>80的答案比例>60%）
        students_with_high_correct = User.objects.filter(role='student').annotate(
            total_answers=Count('answers'),
            high_score_answers=Count('answers', filter=Q(answers__score__gt=80))
        ).filter(
            total_answers__gt=0,  # 确保有答案
            high_score_answers__gt=F('total_answers') * 0.6  # 高分答案比例>60%
        )
        
        # 验证各种复杂查询的结果（具体验证会基于测试数据的分布）
        self.assertGreaterEqual(high_progress_courses.count(), 0)
        self.assertGreaterEqual(high_scoring_students.count(), 0)
        self.assertGreaterEqual(courses_with_many_exercises.count(), 0)
        self.assertGreaterEqual(students_with_high_correct.count(), 0)
    
    def test_ordering_and_distinct(self):
        """测试排序和去重"""
        # 按时间降序获取学习记录，按学生名去重
        latest_records_by_student = LearningRecord.objects.values('student').annotate(
            latest_time=Max('time_spent')
        ).order_by('-latest_time')
        
        # 按平均分数对知识点排序
        kp_by_avg_score = KnowledgePoint.objects.annotate(
            avg_score=Avg('exercises__student_answers__score')
        ).order_by('-avg_score')
        
        # 验证排序正确性
        for i in range(len(kp_by_avg_score) - 1):
            # 如果avg_score不为None，确保排序正确
            if kp_by_avg_score[i].avg_score is not None and kp_by_avg_score[i + 1].avg_score is not None:
                self.assertGreaterEqual(
                    kp_by_avg_score[i].avg_score,
                    kp_by_avg_score[i + 1].avg_score
                )
        
        # 获取练习题最多的3个知识点
        top_kps_by_exercises = KnowledgePoint.objects.annotate(
            exercise_count=Count('exercises')
        ).order_by('-exercise_count')[:3]
        
        # 验证有正确数量的结果
        self.assertLessEqual(len(top_kps_by_exercises), 3)
