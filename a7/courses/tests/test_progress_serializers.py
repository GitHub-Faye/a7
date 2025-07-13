from django.test import TestCase
from django.utils import timezone
from courses.models import Course, KnowledgePoint, Exercise, StudentAnswer, LearningRecord, CourseProgress
from courses.serializers_progress import (
    KnowledgePointProgressSerializer, ExerciseProgressSerializer,
    StudentAnswerSerializer, LearningRecordSerializer,
    LearningRecordUpdateSerializer, CourseProgressSerializer,
    CourseProgressDetailSerializer
)
from users.models import User


class ProgressSerializersTest(TestCase):
    """测试学习进度跟踪相关的序列化器"""
    
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
        
        # 创建测试练习题
        self.exercise1 = Exercise.objects.create(
            title='练习题1',
            content='练习题1的内容',
            type='single_choice',
            difficulty=2,
            knowledge_point=self.kp1,
            answer_template='{"options": ["A", "B", "C", "D"], "answer": "A"}',
            is_required=True,
            correct_count=5,
            attempt_count=10
        )
        
        # 创建测试答案
        self.answer1 = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise1,
            content='{"answer": "A"}',
            score=8.0,
            is_correct=True,
            feedback='很好的回答'
        )
        
        # 创建学习记录
        self.learning_record = LearningRecord.objects.create(
            student=self.student,
            course=self.course,
            knowledge_point=self.kp1,
            status='in_progress',
            progress=65.0,
            time_spent=45
        )
        
        # 创建课程进度
        self.course_progress = CourseProgress.objects.create(
            student=self.student,
            course=self.course,
            overall_progress=65.0,
            required_completed=False,
            correctness_rate=80.0,
            total_time_spent=45
        )
        
    def test_knowledge_point_serializer(self):
        """测试知识点进度序列化器"""
        serializer = KnowledgePointProgressSerializer(instance=self.kp1)
        data = serializer.data
        
        self.assertEqual(data['id'], self.kp1.id)
        self.assertEqual(data['title'], '知识点1')
        self.assertEqual(data['is_required'], True)
        self.assertEqual(data['estimated_time'], 30)
        
        # 测试只能修改部分字段
        update_data = {
            'id': self.kp1.id + 100,  # 不应该被更新
            'title': '修改后的标题',  # 不应该被更新
            'is_required': False,     # 应该被更新
            'estimated_time': 45      # 应该被更新
        }
        
        serializer = KnowledgePointProgressSerializer(instance=self.kp1, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_kp = serializer.save()
        
        self.assertEqual(updated_kp.id, self.kp1.id)  # ID不变
        self.assertEqual(updated_kp.title, '知识点1')  # 标题不变
        self.assertEqual(updated_kp.is_required, False)  # is_required更新
        self.assertEqual(updated_kp.estimated_time, 45)  # estimated_time更新
        
    def test_exercise_serializer(self):
        """测试练习题进度序列化器"""
        # 先重新获取exercise对象，确保包含可能被StudentAnswer创建影响的更新
        self.exercise1.refresh_from_db()
        
        serializer = ExerciseProgressSerializer(instance=self.exercise1)
        data = serializer.data
        
        self.assertEqual(data['id'], self.exercise1.id)
        self.assertEqual(data['title'], '练习题1')
        self.assertEqual(data['type'], 'single_choice')
        self.assertEqual(data['difficulty'], 2)
        self.assertEqual(data['is_required'], True)
        self.assertEqual(data['correct_count'], self.exercise1.correct_count)  # 使用数据库中的实际值
        self.assertEqual(data['attempt_count'], self.exercise1.attempt_count)  # 使用数据库中的实际值
        self.assertEqual(data['correctness_rate'], self.exercise1.correctness_rate)  # 使用模型的属性方法
        
        # 记录当前值，用于后续比较
        current_correct_count = self.exercise1.correct_count
        
        # 测试只能修改is_required字段
        update_data = {
            'title': '修改后的标题',  # 不应该被更新
            'is_required': False,     # 应该被更新
            'correct_count': 100      # 不应该被更新
        }
        
        serializer = ExerciseProgressSerializer(instance=self.exercise1, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_exercise = serializer.save()
        
        self.assertEqual(updated_exercise.title, '练习题1')  # 标题不变
        self.assertEqual(updated_exercise.is_required, False)  # is_required更新
        self.assertEqual(updated_exercise.correct_count, current_correct_count)  # correct_count不变
        
    def test_student_answer_serializer(self):
        """测试学生答案序列化器"""
        serializer = StudentAnswerSerializer(instance=self.answer1)
        data = serializer.data
        
        self.assertEqual(data['id'], self.answer1.id)
        self.assertEqual(data['exercise'], self.exercise1.id)
        self.assertEqual(data['exercise_title'], '练习题1')
        self.assertEqual(data['content'], '{"answer": "A"}')
        self.assertEqual(data['score'], 8.0)
        self.assertEqual(data['is_correct'], True)
        self.assertEqual(data['feedback'], '很好的回答')
        self.assertIn('submitted_at', data)
        
        # 测试更新功能
        update_data = {
            'content': '{"answer": "B"}',
            'score': 6.0,
            'is_correct': False,
            'feedback': '答案需要改进'
        }
        
        serializer = StudentAnswerSerializer(instance=self.answer1, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_answer = serializer.save()
        
        self.assertEqual(updated_answer.content, '{"answer": "B"}')
        self.assertEqual(updated_answer.score, 6.0)
        self.assertEqual(updated_answer.is_correct, False)
        self.assertEqual(updated_answer.feedback, '答案需要改进')
        
    def test_learning_record_serializer(self):
        """测试学习记录序列化器"""
        serializer = LearningRecordSerializer(instance=self.learning_record)
        data = serializer.data
        
        self.assertEqual(data['id'], self.learning_record.id)
        self.assertEqual(data['student'], self.student.id)
        self.assertEqual(data['course'], self.course.id)
        self.assertEqual(data['knowledge_point'], self.kp1.id)
        self.assertEqual(data['knowledge_point_title'], '知识点1')
        self.assertEqual(data['status'], 'in_progress')
        self.assertEqual(data['progress'], 65.0)
        self.assertEqual(data['time_spent'], 45)
        self.assertEqual(data['is_complete'], False)
        self.assertIn('last_accessed', data)
        
        # 测试更新序列化器
        update_data = {
            'progress': 100.0,
            'status': 'completed',
            'time_spent': 60
        }
        
        serializer = LearningRecordUpdateSerializer(instance=self.learning_record, data=update_data)
        self.assertTrue(serializer.is_valid())
        updated_record = serializer.save()
        
        self.assertEqual(updated_record.progress, 100.0)
        self.assertEqual(updated_record.status, 'completed')
        self.assertEqual(updated_record.time_spent, 60)
        self.assertEqual(updated_record.is_complete, True)  # 属性方法应该返回True
        
    def test_course_progress_serializer(self):
        """测试课程进度序列化器"""
        serializer = CourseProgressSerializer(instance=self.course_progress)
        data = serializer.data
        
        self.assertEqual(data['id'], self.course_progress.id)
        self.assertEqual(data['student'], self.student.id)
        self.assertEqual(data['student_name'], 'student')
        self.assertEqual(data['course'], self.course.id)
        self.assertEqual(data['course_title'], '测试课程')
        self.assertEqual(data['overall_progress'], 65.0)
        self.assertEqual(data['required_completed'], False)
        self.assertEqual(data['correctness_rate'], 80.0)
        self.assertEqual(data['total_time_spent'], 45)
        self.assertEqual(data['is_completed'], False)
        self.assertIsNone(data['completion_date'])
        self.assertIn('last_activity', data)
        
    def test_course_progress_detail_serializer(self):
        """测试课程进度详细序列化器"""
        serializer = CourseProgressDetailSerializer(instance=self.course_progress)
        data = serializer.data
        
        # 基本字段
        self.assertEqual(data['id'], self.course_progress.id)
        self.assertEqual(data['student'], self.student.id)
        self.assertEqual(data['course'], self.course.id)
        
        # 关联的学习记录
        self.assertIn('learning_records', data)
        self.assertEqual(len(data['learning_records']), 1)
        self.assertEqual(data['learning_records'][0]['id'], self.learning_record.id)
        self.assertEqual(data['learning_records'][0]['progress'], 65.0)
        
        # 关联的答案
        self.assertIn('answers', data)
        self.assertEqual(len(data['answers']), 1)
        self.assertEqual(data['answers'][0]['id'], self.answer1.id)
        self.assertEqual(data['answers'][0]['score'], 8.0)
        
    def test_learning_record_update_serializer(self):
        """测试学习记录更新序列化器验证"""
        # 测试正常范围内的数据
        valid_data = {'progress': 75.0, 'time_spent': 30}
        serializer = LearningRecordUpdateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # 测试进度超出范围的数据
        invalid_progress = {'progress': 150.0, 'time_spent': 30}
        serializer = LearningRecordUpdateSerializer(data=invalid_progress)
        self.assertFalse(serializer.is_valid())
        self.assertIn('progress', serializer.errors)
        
        # 测试负时间的数据
        invalid_time = {'progress': 50.0, 'time_spent': -10}
        serializer = LearningRecordUpdateSerializer(data=invalid_time)
        self.assertFalse(serializer.is_valid())
        self.assertIn('time_spent', serializer.errors)
        
        # 测试无效状态值
        invalid_status = {'status': 'invalid_status', 'progress': 50.0}
        serializer = LearningRecordUpdateSerializer(data=invalid_status)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors) 