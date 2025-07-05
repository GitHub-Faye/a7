from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from .models import Course, KnowledgePoint, Exercise, StudentAnswer
from .serializers import (
    ExerciseSerializer, ExerciseCreateSerializer, ExerciseUpdateSerializer,
    StudentAnswerSerializer, StudentAnswerCreateSerializer, StudentAnswerUpdateSerializer,
    StudentAnswerFeedbackSerializer
)

User = get_user_model()

class ExerciseSerializerTests(TestCase):
    """测试Exercise相关的序列化器"""
    
    def setUp(self):
        # 创建测试用户
        self.teacher = User.objects.create_user(
            username='teacher',
            password='password123',
            email='teacher@example.com',
            role='teacher'
        )
        
        # 创建课程
        self.course = Course.objects.create(
            title='测试课程',
            description='测试课程描述',
            subject='数学',
            grade_level='高中一年级',
            teacher=self.teacher
        )
        
        # 创建知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='三角函数',
            content='三角函数的基本概念和性质',
            importance=8
        )
        
        # 创建练习题
        self.exercise = Exercise.objects.create(
            title='测试练习题',
            content='求正弦函数sin(30°)的值',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template='{"options": ["0.5", "1", "0", "2"], "correct": "0.5"}'
        )
        
        # 创建请求工厂
        self.factory = APIRequestFactory()

    def test_exercise_serializer(self):
        """测试练习题序列化器读取功能"""
        serializer = ExerciseSerializer(self.exercise)
        data = serializer.data
        
        self.assertEqual(data['id'], self.exercise.id)
        self.assertEqual(data['title'], '测试练习题')
        self.assertEqual(data['content'], '求正弦函数sin(30°)的值')
        self.assertEqual(data['type'], 'single_choice')
        self.assertEqual(data['type_display'], '单选题')
        self.assertEqual(data['difficulty'], 3)
        self.assertEqual(data['difficulty_display'], '中等')
        self.assertEqual(data['knowledge_point'], self.knowledge_point.id)
        self.assertEqual(data['knowledge_point_title'], '三角函数')
        self.assertEqual(data['answer_template'], '{"options": ["0.5", "1", "0", "2"], "correct": "0.5"}')
    
    def test_exercise_create_serializer_valid(self):
        """测试练习题创建序列化器的有效数据"""
        request = self.factory.post('/api/exercises/')
        request.user = self.teacher
        
        data = {
            'title': '新练习题',
            'content': '计算2+2的值',
            'type': 'single_choice',
            'difficulty': 1,
            'knowledge_point': self.knowledge_point.id,
            'answer_template': '{"options": ["3", "4", "5", "6"], "correct": "4"}'
        }
        
        serializer = ExerciseCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_exercise_create_serializer_invalid(self):
        """测试练习题创建序列化器的无效数据"""
        request = self.factory.post('/api/exercises/')
        request.user = self.teacher
        
        # 标题为空
        data = {
            'title': '',
            'content': '计算2+2的值',
            'type': 'single_choice',
            'difficulty': 1,
            'knowledge_point': self.knowledge_point.id
        }
        
        serializer = ExerciseCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # 无效的题目类型
        data = {
            'title': '新练习题',
            'content': '计算2+2的值',
            'type': 'invalid_type',
            'difficulty': 1,
            'knowledge_point': self.knowledge_point.id
        }
        
        serializer = ExerciseCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('type', serializer.errors)
        
        # 无效的难度等级
        data = {
            'title': '新练习题',
            'content': '计算2+2的值',
            'type': 'single_choice',
            'difficulty': 10,  # 超出1-5范围
            'knowledge_point': self.knowledge_point.id
        }
        
        serializer = ExerciseCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('difficulty', serializer.errors)
        
        # 标题重复
        data = {
            'title': '测试练习题',  # 与setUp中创建的练习题标题相同
            'content': '计算2+2的值',
            'type': 'single_choice',
            'difficulty': 1,
            'knowledge_point': self.knowledge_point.id
        }
        
        serializer = ExerciseCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_exercise_update_serializer(self):
        """测试练习题更新序列化器"""
        request = self.factory.put(f'/api/exercises/{self.exercise.id}/')
        request.user = self.teacher
        
        data = {
            'title': '更新后的练习题',
            'content': '更新后的内容',
            'type': 'multiple_choice',
            'difficulty': 4,
            'answer_template': '{"options": ["选项A", "选项B"], "correct": ["选项A"]}'
        }
        
        serializer = ExerciseUpdateSerializer(
            instance=self.exercise,
            data=data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_exercise = serializer.save()
        
        self.assertEqual(updated_exercise.title, '更新后的练习题')
        self.assertEqual(updated_exercise.content, '更新后的内容')
        self.assertEqual(updated_exercise.type, 'multiple_choice')
        self.assertEqual(updated_exercise.difficulty, 4)
        self.assertEqual(updated_exercise.answer_template, '{"options": ["选项A", "选项B"], "correct": ["选项A"]}')


class StudentAnswerSerializerTests(TestCase):
    """测试StudentAnswer相关的序列化器"""
    
    def setUp(self):
        # 创建测试用户
        self.teacher = User.objects.create_user(
            username='teacher',
            password='password123',
            email='teacher@example.com',
            role='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student',
            password='password123',
            email='student@example.com',
            role='student',
            first_name='张',
            last_name='三'
        )
        
        # 创建课程
        self.course = Course.objects.create(
            title='测试课程',
            description='测试课程描述',
            subject='数学',
            grade_level='高中一年级',
            teacher=self.teacher
        )
        
        # 创建知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title='三角函数',
            content='三角函数的基本概念和性质',
            importance=8
        )
        
        # 创建练习题
        self.exercise = Exercise.objects.create(
            title='测试练习题',
            content='求正弦函数sin(30°)的值',
            type='single_choice',
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template='{"options": ["0.5", "1", "0", "2"], "correct": "0.5"}'
        )
        
        # 创建学生答案
        self.student_answer = StudentAnswer.objects.create(
            student=self.student,
            exercise=self.exercise,
            content='0.5',
            score=10.0,
            feedback='正确！'
        )
        
        # 创建请求工厂
        self.factory = APIRequestFactory()

    def test_student_answer_serializer(self):
        """测试学生答案序列化器读取功能"""
        serializer = StudentAnswerSerializer(self.student_answer)
        data = serializer.data
        
        self.assertEqual(data['id'], self.student_answer.id)
        self.assertEqual(data['student'], self.student.id)
        self.assertEqual(data['student_name'], '张三')
        self.assertEqual(data['exercise'], self.exercise.id)
        self.assertEqual(data['exercise_title'], '测试练习题')
        self.assertEqual(data['content'], '0.5')
        self.assertEqual(data['score'], 10.0)
        self.assertEqual(data['feedback'], '正确！')
    
    def test_student_answer_create_serializer(self):
        """测试学生答案创建序列化器"""
        # 创建另一个练习题，避免与现有答案冲突
        another_exercise = Exercise.objects.create(
            title='另一个练习题',
            content='计算2+2的值',
            type='single_choice',
            difficulty=1,
            knowledge_point=self.knowledge_point,
            answer_template='{"options": ["3", "4", "5", "6"], "correct": "4"}'
        )
        
        request = self.factory.post('/api/student-answers/')
        request.user = self.student
        
        data = {
            'exercise': another_exercise.id,
            'content': '4'
        }
        
        serializer = StudentAnswerCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        student_answer = serializer.save()
        self.assertEqual(student_answer.student, self.student)
        self.assertEqual(student_answer.exercise, another_exercise)
        self.assertEqual(student_answer.content, '4')
    
    def test_student_answer_create_duplicate(self):
        """测试学生答案创建序列化器 - 重复提交"""
        request = self.factory.post('/api/student-answers/')
        request.user = self.student
        
        # 尝试为已回答的练习题再次提交答案
        data = {
            'exercise': self.exercise.id,
            'content': '不同的答案'
        }
        
        serializer = StudentAnswerCreateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('exercise', serializer.errors)
    
    def test_student_answer_update_serializer(self):
        """测试学生答案更新序列化器"""
        request = self.factory.put(f'/api/student-answers/{self.student_answer.id}/')
        request.user = self.student
        
        data = {
            'content': '修改后的答案'
        }
        
        serializer = StudentAnswerUpdateSerializer(
            instance=self.student_answer,
            data=data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_answer = serializer.save()
        self.assertEqual(updated_answer.content, '修改后的答案')
    
    def test_student_answer_feedback_serializer(self):
        """测试学生答案反馈序列化器"""
        request = self.factory.put(f'/api/student-answers/{self.student_answer.id}/feedback/')
        request.user = self.teacher
        
        data = {
            'score': 90.5,
            'feedback': '非常好的答案，但还有改进空间'
        }
        
        serializer = StudentAnswerFeedbackSerializer(
            instance=self.student_answer,
            data=data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_answer = serializer.save()
        self.assertEqual(updated_answer.score, 90.5)
        self.assertEqual(updated_answer.feedback, '非常好的答案，但还有改进空间')
    
    def test_student_answer_feedback_invalid_score(self):
        """测试学生答案反馈序列化器 - 无效的分数"""
        request = self.factory.put(f'/api/student-answers/{self.student_answer.id}/feedback/')
        request.user = self.teacher
        
        # 分数超出0-100范围
        data = {
            'score': 101,
            'feedback': '反馈'
        }
        
        serializer = StudentAnswerFeedbackSerializer(
            instance=self.student_answer,
            data=data,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('score', serializer.errors) 