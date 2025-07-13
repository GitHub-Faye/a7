from django.test import TestCase
from django.utils import timezone
from courses.models import Course, KnowledgePoint, Exercise, StudentAnswer, LearningRecord, CourseProgress
from users.models import User
import datetime

class ProgressTrackingModelsTest(TestCase):
    """测试学习进度跟踪相关模型的功能"""
    
    def setUp(self):
        # 创建测试用户
        self.teacher = User.objects.create_user(username='teacher', password='password')
        self.student = User.objects.create_user(username='student', password='password')
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='计算机科学',
            grade_level='大学一年级',
            teacher=self.teacher
        )
        
        # 创建测试知识点
        self.kp1 = KnowledgePoint.objects.create(
            course=self.course,
            title='知识点1',
            content='知识点1的内容',
            importance=5,
            is_required=True,
            estimated_time=30
        )
        
        self.kp2 = KnowledgePoint.objects.create(
            course=self.course,
            title='知识点2',
            content='知识点2的内容',
            importance=3,
            parent=self.kp1,
            is_required=False,
            estimated_time=20
        )
        
        # 创建测试练习题
        self.exercise1 = Exercise.objects.create(
            title='练习题1',
            content='练习题1的内容',
            type='single_choice',
            difficulty=2,
            knowledge_point=self.kp1,
            answer_template='{"options": ["A", "B", "C", "D"], "answer": "A"}',
            is_required=True
        )
        
        self.exercise2 = Exercise.objects.create(
            title='练习题2',
            content='练习题2的内容',
            type='short_answer',
            difficulty=4,
            knowledge_point=self.kp2,
            answer_template='示例答案',
            is_required=False
        )
        
        # 创建学习记录
        self.lr1 = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=self.kp1,
            status='in_progress',
            progress=50.0,
            time_spent=15
        )
        
    def test_field_extensions(self):
        """测试新增字段的功能"""
        # 测试知识点扩展字段
        self.assertTrue(self.kp1.is_required)
        self.assertEqual(self.kp1.estimated_time, 30)
        self.assertFalse(self.kp2.is_required)
        self.assertEqual(self.kp2.estimated_time, 20)
        
        # 测试练习题扩展字段
        self.assertTrue(self.exercise1.is_required)
        self.assertEqual(self.exercise1.correct_count, 0)
        self.assertEqual(self.exercise1.attempt_count, 0)
        
    def test_student_answer_update_statistics(self):
        """测试学生回答更新练习题统计信息"""
        # 创建正确答案
        answer1 = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise1,
            content='{"answer": "A"}',
            score=10.0,
            is_correct=True
        )
        
        # 检查练习题统计信息是否更新
        self.exercise1.refresh_from_db()
        self.assertEqual(self.exercise1.correct_count, 1)
        self.assertEqual(self.exercise1.attempt_count, 1)
        self.assertEqual(self.exercise1.correctness_rate, 100.0)
        
        # 创建错误答案
        answer2 = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise2,
            content='错误答案',
            score=0.0,
            is_correct=False
        )
        
        # 检查练习题统计信息是否更新
        self.exercise2.refresh_from_db()
        self.assertEqual(self.exercise2.correct_count, 0)
        self.assertEqual(self.exercise2.attempt_count, 1)
        self.assertEqual(self.exercise2.correctness_rate, 0.0)
        
        # 更新答案并检查统计信息变化
        answer2.is_correct = True
        answer2.score = 8.0
        answer2.save()
        
        self.exercise2.refresh_from_db()
        self.assertEqual(self.exercise2.correct_count, 1)
        self.assertEqual(self.exercise2.attempt_count, 1)  # 不应再增加
        self.assertEqual(self.exercise2.correctness_rate, 100.0)
    
    def test_course_progress_creation(self):
        """测试更新学习记录时自动创建和更新课程进度"""
        # 初始状态下不应该有课程进度记录
        self.assertEqual(CourseProgress.objects.count(), 0)
        
        # 更新学习记录，应该触发课程进度创建
        self.lr1.update_progress(75.0)
        
        # 检查课程进度是否被创建
        self.assertEqual(CourseProgress.objects.count(), 1)
        course_progress = CourseProgress.objects.first()
        
        # 验证课程进度数据
        self.assertEqual(course_progress.student, self.student)
        self.assertEqual(course_progress.course, self.course)
        self.assertAlmostEqual(course_progress.overall_progress, 75.0)
        self.assertEqual(course_progress.total_time_spent, 15)
        
        # 添加更多学习时间，检查进度更新
        self.lr1.add_time_spent(30)
        
        # 重新获取课程进度
        course_progress.refresh_from_db()
        self.assertEqual(course_progress.total_time_spent, 45)
        
    def test_course_progress_completion(self):
        """测试课程完成的状态更新"""
        # 更新学习记录为完成状态
        self.lr1.update_progress(100.0)
        
        # 检查课程进度
        course_progress = CourseProgress.objects.first()
        
        # 由于只完成了一个必修知识点中的一个，所以课程应该标记为已完成
        self.assertTrue(course_progress.is_completed)
        self.assertIsNotNone(course_progress.completion_date)
        self.assertTrue(course_progress.required_completed)
        
        # 添加另一个必修知识点的学习记录，但未完成
        kp3 = KnowledgePoint.objects.create(
            course=self.course,
            title='知识点3',
            content='知识点3的内容',
            importance=4,
            is_required=True
        )
        
        lr2 = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=kp3,
            status='in_progress',
            progress=30.0
        )
        
        # 由于未完成所有必修知识点，课程进度应更新为未完成
        lr2._update_course_progress()
        course_progress.refresh_from_db()
        
        # 因为是新增的知识点未完成，所以必修内容不再全部完成
        self.assertFalse(course_progress.required_completed)
        
        # 计算整体进度应该是两个知识点的平均值
        expected_progress = (100.0 + 30.0) / 2  # 两个知识点的平均进度
        self.assertAlmostEqual(course_progress.overall_progress, expected_progress)
        
    def test_correctness_rate_calculation(self):
        """测试正确率计算"""
        # 创建一些答案记录
        StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise1,
            content='{"answer": "A"}',
            score=10.0,
            is_correct=True
        )
        
        StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise2,
            content='错误答案',
            score=0.0,
            is_correct=False
        )
        
        # 触发课程进度更新
        self.lr1.update_progress(60.0)
        
        # 检查正确率计算
        course_progress = CourseProgress.objects.first()
        self.assertAlmostEqual(course_progress.correctness_rate, 50.0)  # 1正确1错误，正确率50%
        
        # 添加更多答案并更新
        exercise3 = Exercise.objects.create(
            title='练习题3',
            content='练习题3的内容',
            type='multiple_choice',
            difficulty=3,
            knowledge_point=self.kp1,
            is_required=True
        )
        
        StudentAnswer.objects.create(
            student=self.student,
            exercise=exercise3,
            content='{"answers": ["A", "C"]}',
            score=8.0,
            is_correct=True
        )
        
        # 触发更新
        self.lr1._update_course_progress()
        
        # 重新获取并检查正确率
        course_progress.refresh_from_db()
        self.assertAlmostEqual(course_progress.correctness_rate, 2/3 * 100)  # 2正确1错误，正确率约66.7% 