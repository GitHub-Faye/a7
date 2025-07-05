from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from courses.models import Course, KnowledgePoint, Exercise, StudentAnswer
from datetime import datetime, timedelta

class ExerciseAPITests(APITestCase):

    def setUp(self):
        """测试准备，创建用户、课程和知识点"""
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        self.knowledge_point2 = KnowledgePoint.objects.create(title='测试知识点2', course=self.course)
        self.exercise_url = reverse('exercise-list')

    def test_create_exercise(self):
        """测试创建练习题"""
        data = {
            'title': '新的练习题',
            'content': '这是一个练习题的内容。',
            'type': 'single_choice',
            'difficulty': 3,
            'knowledge_point': self.knowledge_point.id
        }
        response = self.client.post(self.exercise_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertEqual(Exercise.objects.get().title, '新的练习题')

    def test_list_exercises(self):
        """测试获取练习题列表"""
        Exercise.objects.create(title='练习题1', knowledge_point=self.knowledge_point)
        Exercise.objects.create(title='练习题2', knowledge_point=self.knowledge_point)
        
        response = self.client.get(self.exercise_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 2)

    def test_retrieve_exercise(self):
        """测试获取单个练习题详情"""
        exercise = Exercise.objects.create(title='详情测试练习题', knowledge_point=self.knowledge_point)
        detail_url = reverse('exercise-detail', kwargs={'pk': exercise.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], '详情测试练习题')

    def test_update_exercise(self):
        """测试更新练习题"""
        exercise = Exercise.objects.create(title='待更新的练习题', knowledge_point=self.knowledge_point)
        detail_url = reverse('exercise-detail', kwargs={'pk': exercise.pk})
        update_data = {'title': '已更新的练习题'}
        
        response = self.client.patch(detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exercise.refresh_from_db()
        self.assertEqual(exercise.title, '已更新的练习题')

    def test_delete_exercise(self):
        """测试删除练习题"""
        exercise = Exercise.objects.create(title='待删除的练习题', knowledge_point=self.knowledge_point)
        detail_url = reverse('exercise-detail', kwargs={'pk': exercise.pk})
        
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Exercise.objects.count(), 0)
        
    def test_filter_exercises_by_knowledge_point(self):
        """测试按知识点过滤练习题"""
        # 创建不同知识点的练习题
        exercise1 = Exercise.objects.create(
            title='知识点1的练习题', 
            content='内容1',
            knowledge_point=self.knowledge_point
        )
        exercise2 = Exercise.objects.create(
            title='知识点2的练习题', 
            content='内容2',
            knowledge_point=self.knowledge_point2
        )
        
        # 按知识点1过滤
        response = self.client.get(f"{self.exercise_url}?knowledge_point={self.knowledge_point.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '知识点1的练习题')
        
        # 按知识点2过滤
        response = self.client.get(f"{self.exercise_url}?knowledge_point={self.knowledge_point2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '知识点2的练习题')
    
    def test_filter_exercises_by_type(self):
        """测试按题目类型过滤练习题"""
        # 创建不同类型的练习题
        exercise1 = Exercise.objects.create(
            title='单选题', 
            content='单选题内容',
            type='single_choice',
            knowledge_point=self.knowledge_point
        )
        exercise2 = Exercise.objects.create(
            title='多选题', 
            content='多选题内容',
            type='multiple_choice',
            knowledge_point=self.knowledge_point
        )
        
        # 按单选题过滤
        response = self.client.get(f"{self.exercise_url}?type=single_choice")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '单选题')
        
        # 按多选题过滤
        response = self.client.get(f"{self.exercise_url}?type=multiple_choice")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '多选题')
    
    def test_filter_exercises_by_difficulty(self):
        """测试按难度过滤练习题"""
        # 创建不同难度的练习题
        exercise1 = Exercise.objects.create(
            title='简单题', 
            content='简单题内容',
            difficulty=1,
            knowledge_point=self.knowledge_point
        )
        exercise2 = Exercise.objects.create(
            title='困难题', 
            content='困难题内容',
            difficulty=5,
            knowledge_point=self.knowledge_point
        )
        
        # 按简单难度过滤
        response = self.client.get(f"{self.exercise_url}?difficulty=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '简单题')
        
        # 按困难难度过滤
        response = self.client.get(f"{self.exercise_url}?difficulty=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '困难题')
    
    def test_search_exercises(self):
        """测试搜索练习题"""
        # 创建含有不同关键词的练习题
        exercise1 = Exercise.objects.create(
            title='数学题目', 
            content='这是一道关于代数的题目',
            knowledge_point=self.knowledge_point
        )
        exercise2 = Exercise.objects.create(
            title='物理题目', 
            content='这是一道关于力学的题目',
            knowledge_point=self.knowledge_point
        )
        
        # 搜索标题中包含"数学"的练习题
        response = self.client.get(f"{self.exercise_url}?search=数学")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '数学题目')
        
        # 搜索内容中包含"力学"的练习题
        response = self.client.get(f"{self.exercise_url}?search=力学")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], '物理题目')
    
    def test_order_exercises(self):
        """测试练习题排序"""
        # 创建具有不同创建时间的练习题
        exercise1 = Exercise.objects.create(
            title='较早的练习题', 
            content='内容1',
            knowledge_point=self.knowledge_point
        )
        # 手动设置创建时间为1天前
        exercise1.created_at = datetime.now() - timedelta(days=1)
        exercise1.save()
        
        exercise2 = Exercise.objects.create(
            title='较新的练习题', 
            content='内容2',
            knowledge_point=self.knowledge_point
        )
        
        # 按创建时间升序排序
        response = self.client.get(f"{self.exercise_url}?ordering=created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['results'][0]['title'], '较早的练习题')
        self.assertEqual(response.data['data']['results'][1]['title'], '较新的练习题')
        
        # 按创建时间降序排序
        response = self.client.get(f"{self.exercise_url}?ordering=-created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['results'][0]['title'], '较新的练习题')
        self.assertEqual(response.data['data']['results'][1]['title'], '较早的练习题')


class StudentAnswerAPITests(APITestCase):

    def setUp(self):
        """测试准备，创建用户、课程、知识点和练习"""
        self.student_user = User.objects.create_user(username='student', password='password', role='student')
        self.student_user2 = User.objects.create_user(username='student2', password='password', role='student')
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        self.exercise = Exercise.objects.create(title='测试练习1', knowledge_point=self.knowledge_point)
        self.exercise2 = Exercise.objects.create(title='测试练习2', knowledge_point=self.knowledge_point)
        self.answer_url = reverse('studentanswer-list')

    def test_create_student_answer(self):
        """测试创建学生答案"""
        data = {
            'student': self.student_user.id,
            'exercise': self.exercise.id,
            'content': '这是学生的答案内容。'
        }
        response = self.client.post(self.answer_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentAnswer.objects.count(), 1)
        self.assertEqual(StudentAnswer.objects.get().content, '这是学生的答案内容。')

    def test_list_student_answers(self):
        """测试获取学生答案列表"""
        StudentAnswer.objects.create(student=self.student_user, exercise=self.exercise, content='答案1')
        StudentAnswer.objects.create(student=self.student_user, exercise=Exercise.objects.create(title='练习2', knowledge_point=self.knowledge_point), content='答案2')
        
        response = self.client.get(self.answer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 2)

    def test_retrieve_student_answer(self):
        """测试获取单个学生答案详情"""
        answer = StudentAnswer.objects.create(student=self.student_user, exercise=self.exercise, content='答案详情')
        detail_url = reverse('studentanswer-detail', kwargs={'pk': answer.pk})
        
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['content'], '答案详情')

    def test_update_student_answer(self):
        """测试更新学生答案"""
        answer = StudentAnswer.objects.create(student=self.student_user, exercise=self.exercise, content='待更新的答案')
        detail_url = reverse('studentanswer-detail', kwargs={'pk': answer.pk})
        update_data = {'content': '已更新的答案'}
        
        response = self.client.patch(detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        answer.refresh_from_db()
        self.assertEqual(answer.content, '已更新的答案')

    def test_delete_student_answer(self):
        """测试删除学生答案"""
        answer = StudentAnswer.objects.create(student=self.student_user, exercise=self.exercise, content='待删除的答案')
        detail_url = reverse('studentanswer-detail', kwargs={'pk': answer.pk})
        
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StudentAnswer.objects.count(), 0)
        
    def test_filter_student_answers_by_student(self):
        """测试按学生过滤答案"""
        # 创建不同学生的答案
        answer1 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise, 
            content='学生1的答案'
        )
        answer2 = StudentAnswer.objects.create(
            student=self.student_user2, 
            exercise=self.exercise, 
            content='学生2的答案'
        )
        
        # 按学生1过滤
        response = self.client.get(f"{self.answer_url}?student={self.student_user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '学生1的答案')
        
        # 按学生2过滤
        response = self.client.get(f"{self.answer_url}?student={self.student_user2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '学生2的答案')
    
    def test_filter_student_answers_by_exercise(self):
        """测试按练习题过滤答案"""
        # 创建不同练习题的答案
        answer1 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise, 
            content='练习1的答案'
        )
        answer2 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise2, 
            content='练习2的答案'
        )
        
        # 按练习1过滤
        response = self.client.get(f"{self.answer_url}?exercise={self.exercise.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '练习1的答案')
        
        # 按练习2过滤
        response = self.client.get(f"{self.answer_url}?exercise={self.exercise2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '练习2的答案')
    
    def test_filter_student_answers_by_score(self):
        """测试按得分过滤答案"""
        # 创建不同得分的答案
        answer1 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise, 
            content='满分答案',
            score=100.0
        )
        answer2 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise2, 
            content='零分答案',
            score=0.0
        )
        
        # 按满分过滤
        response = self.client.get(f"{self.answer_url}?score=100.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '满分答案')
        
        # 按零分过滤
        response = self.client.get(f"{self.answer_url}?score=0.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '零分答案')
    
    def test_search_student_answers(self):
        """测试搜索学生答案"""
        # 创建含有不同关键词的答案
        answer1 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise, 
            content='这是一个关于数学的答案'
        )
        answer2 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise2, 
            content='这是一个关于物理的答案'
        )
        
        # 搜索内容中包含"数学"的答案
        response = self.client.get(f"{self.answer_url}?search=数学")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '这是一个关于数学的答案')
        
        # 搜索内容中包含"物理"的答案
        response = self.client.get(f"{self.answer_url}?search=物理")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['content'], '这是一个关于物理的答案')
    
    def test_order_student_answers(self):
        """测试学生答案排序"""
        # 创建具有不同提交时间的答案
        answer1 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise, 
            content='较早的答案'
        )
        # 手动设置提交时间为1天前
        answer1.submitted_at = datetime.now() - timedelta(days=1)
        answer1.save()
        
        answer2 = StudentAnswer.objects.create(
            student=self.student_user, 
            exercise=self.exercise2, 
            content='较新的答案'
        )
        
        # 按提交时间升序排序
        response = self.client.get(f"{self.answer_url}?ordering=submitted_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['results'][0]['content'], '较早的答案')
        self.assertEqual(response.data['data']['results'][1]['content'], '较新的答案')
        
        # 按提交时间降序排序
        response = self.client.get(f"{self.answer_url}?ordering=-submitted_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['results'][0]['content'], '较新的答案')
        self.assertEqual(response.data['data']['results'][1]['content'], '较早的答案') 