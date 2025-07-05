from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from courses.models import Course, KnowledgePoint, Exercise, StudentAnswer

class ExerciseAPITests(APITestCase):

    def setUp(self):
        """测试准备，创建用户、课程和知识点"""
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
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

class StudentAnswerAPITests(APITestCase):

    def setUp(self):
        """测试准备，创建用户、课程、知识点和练习"""
        self.student_user = User.objects.create_user(username='student', password='password', role='student')
        self.teacher_user = User.objects.create_user(username='teacher', password='password', role='teacher')
        
        self.course = Course.objects.create(title='测试课程', teacher=self.teacher_user)
        self.knowledge_point = KnowledgePoint.objects.create(title='测试知识点', course=self.course)
        self.exercise = Exercise.objects.create(title='测试练习', knowledge_point=self.knowledge_point)
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