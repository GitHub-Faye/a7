from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta

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
