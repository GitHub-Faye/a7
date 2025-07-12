"""
学生助手模块集成测试模块

测试AI对话、练习生成和答案校正组件作为统一系统的集成功能
"""

import json
import uuid
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Course, KnowledgePoint, Exercise
from users.models import User
from ai_services.services.n8n_webhook.exceptions import N8nWebhookError


class StudentAssistantIntegrationTests(TestCase):
    """学生助手模块集成测试类"""
    
    def setUp(self):
        """设置测试环境，创建必要的测试数据"""
        # 创建API客户端
        self.client = APIClient()
        
        # API端点
        self.dialogue_url = reverse('student-dialogue-list')
        self.exercise_url = reverse('ai_services:generate-exercises-list')
        self.correction_url = reverse('ai_services:correct-answer-list')
        
        # 创建测试课程和知识点
        self.teacher = User.objects.create_user(username='teacher1', password='password123')
        self.course = Course.objects.create(
            title="测试课程", 
            description="测试课程描述",
            subject="物理",
            grade_level="高中",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="牛顿运动定律",
            content="牛顿运动定律是经典力学的基础，包括三个定律...",
            importance=5
        )
        
        # 创建测试练习题
        self.exercise = Exercise.objects.create(
            title="牛顿第二定律应用题",
            content="一个5kg的物体在10N力的作用下，其加速度是多少?",
            type="short_answer",
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template="2 m/s^2"
        )
        
        # 模拟响应数据
        self.mock_dialogue_response = {
            'answer': '牛顿第二定律指出，物体的加速度等于作用在它上面的力除以它的质量(a = F/m)。',
            'resources': [
                {
                    'title': '牛顿运动定律',
                    'content': '牛顿运动定律简介',
                    'type': '知识点',
                    'id': self.knowledge_point.id
                }
            ],
            'follow_up_questions': ['什么是牛顿第三定律？', '惯性是什么？']
        }
        
        self.mock_exercises_response = {
            "questions": [
                {
                    "title": "牛顿第二定律计算题",
                    "content": "一个10kg的物体受到20N的力，求加速度。",
                    "type": "short_answer",
                    "difficulty": 3,
                    "answer_template": "2 m/s^2",
                    "knowledge_point_id": self.knowledge_point.id
                }
            ],
            "session_id": "test-session-id"
        }
        
        self.mock_correction_response = {
            "is_correct": True,
            "score": 100,
            "feedback": "回答正确！根据牛顿第二定律，a = F/m = 10N/5kg = 2 m/s^2",
            "improvement_suggestions": "可以尝试解决更复杂的问题",
            "explanation": "牛顿第二定律表述为F = ma，其中F是力，m是质量，a是加速度。"
        }

    @patch('ai_services.views.N8nWebhookClient')
    def test_complete_workflow(self, mock_client_class):
        """测试完整的对话->练习->答案流程"""
        # 设置模拟客户端的返回值
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        # 配置模拟方法返回值
        mock_client_instance.dialogue_with_student_sync.return_value = self.mock_dialogue_response
        mock_client_instance.generate_exercises_sync.return_value = self.mock_exercises_response
        mock_client_instance.correct_student_answer_sync.return_value = self.mock_correction_response
        
        # 步骤1: 发起对话
        session_id = str(uuid.uuid4())
        dialogue_data = {
            'query': '请解释牛顿第二定律',
            'session_id': session_id
        }
        
        dialogue_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(dialogue_data),
            content_type='application/json'
        )
        
        # 验证对话响应
        self.assertEqual(dialogue_response.status_code, status.HTTP_200_OK)
        self.assertTrue(dialogue_response.data['success'])
        self.assertEqual(dialogue_response.data['data']['answer'], self.mock_dialogue_response['answer'])
        
        # 步骤2: 请求生成练习题
        exercise_data = {
            'query': '生成关于牛顿第二定律的练习题',
            'knowledge_point_ids': [self.knowledge_point.id],
            'session_id': session_id
        }
        
        exercise_response = self.client.post(
            self.exercise_url,
            data=json.dumps(exercise_data),
            content_type='application/json'
        )
        
        # 验证练习题响应
        self.assertEqual(exercise_response.status_code, status.HTTP_200_OK)
        self.assertTrue(exercise_response.data['success'])
        self.assertEqual(len(exercise_response.data['data']['exercises']), 1)
        
        # 从响应中提取练习题
        generated_exercise = exercise_response.data['data']['exercises'][0]
        
        # 步骤3: 提交答案并获取反馈
        correction_data = {
            'exercise_id': self.exercise.id,  # 使用预设的练习题
            'student_answer': '2 m/s^2',
            'session_id': session_id
        }
        
        correction_response = self.client.post(
            self.correction_url,
            data=json.dumps(correction_data),
            content_type='application/json'
        )
        
        # 验证答案校正响应
        self.assertEqual(correction_response.status_code, status.HTTP_200_OK)
        self.assertTrue(correction_response.data['success'])
        self.assertTrue(correction_response.data['data']['is_correct'])
        
        # 步骤4: 继续对话，讨论答案
        follow_up_data = {
            'query': '你能解释为什么答案是2 m/s^2吗?',
            'session_id': session_id  # 使用相同的会话ID
        }
        
        follow_up_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(follow_up_data),
            content_type='application/json'
        )
        
        # 验证后续对话响应
        self.assertEqual(follow_up_response.status_code, status.HTTP_200_OK)
        self.assertTrue(follow_up_response.data['success'])
        
        # 验证整个流程中会话ID的一致性
        self.assertEqual(dialogue_response.data['data']['session_id'], session_id)
        self.assertEqual(exercise_response.data['data']['session_id'], session_id)
        self.assertEqual(correction_response.data['data']['session_id'], session_id)
        self.assertEqual(follow_up_response.data['data']['session_id'], session_id)
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_session_management(self, mock_client_class):
        """测试会话ID管理和持久性"""
        # 设置模拟客户端
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        mock_client_instance.dialogue_with_student_sync.return_value = self.mock_dialogue_response
        
        # 测试1: 不提供会话ID，应自动生成
        auto_session_data = {
            'query': '什么是牛顿第一定律?'
        }
        
        auto_session_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(auto_session_data),
            content_type='application/json'
        )
        
        self.assertEqual(auto_session_response.status_code, status.HTTP_200_OK)
        self.assertIn('session_id', auto_session_response.data['data'])
        auto_generated_id = auto_session_response.data['data']['session_id']
        self.assertIsNotNone(auto_generated_id)
        
        # 测试2: 使用上一步自动生成的会话ID继续对话
        follow_up_data = {
            'query': '请继续解释惯性',
            'session_id': auto_generated_id
        }
        
        follow_up_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(follow_up_data),
            content_type='application/json'
        )
        
        self.assertEqual(follow_up_response.status_code, status.HTTP_200_OK)
        self.assertEqual(follow_up_response.data['data']['session_id'], auto_generated_id)
        
        # 测试3: 会话超时模拟
        # 由于这是单元测试环境，我们模拟超时情况，让客户端在处理带有特定会话ID的请求时抛出会话超时错误
        timeout_session_id = "expired-session-id"
        mock_client_instance.dialogue_with_student_sync.side_effect = lambda x: (
            N8nWebhookError("Session expired") 
            if x.get('sessionId') == timeout_session_id 
            else self.mock_dialogue_response
        )
        
        timeout_data = {
            'query': '牛顿第三定律是什么?',
            'session_id': timeout_session_id
        }
        
        timeout_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(timeout_data),
            content_type='application/json'
        )
        
        self.assertEqual(timeout_response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(timeout_response.data['success'])
        
        # 恢复正常行为
        mock_client_instance.dialogue_with_student_sync.side_effect = None
        mock_client_instance.dialogue_with_student_sync.return_value = self.mock_dialogue_response

    @patch('ai_services.views.N8nWebhookClient')
    def test_dialogue_exercise_interaction(self, mock_client_class):
        """测试通过对话请求生成练习题并继续对话的能力"""
        # 设置模拟客户端
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        # 配置dialogue_with_student_sync模拟方法，根据查询内容返回不同响应
        def dialogue_side_effect(request_data):
            query = request_data.get('query', '').lower()
            if '生成练习题' in query:
                # 对话中请求生成练习题
                return {
                    'answer': '我已为你生成关于牛顿第二定律的练习题。',
                    'resources': [],
                    'follow_up_questions': [],
                    'exercise_request': {
                        'knowledge_point_ids': [self.knowledge_point.id],
                        'quantity': 2,
                        'difficulty': 3
                    }
                }
            elif '解释答案' in query:
                # 讨论答案的对话
                return {
                    'answer': '根据牛顿第二定律F=ma，可以得出a=F/m=10N/5kg=2 m/s^2',
                    'resources': [
                        {
                            'title': '牛顿运动定律',
                            'content': '牛顿运动定律应用',
                            'type': '知识点',
                            'id': self.knowledge_point.id
                        }
                    ],
                    'follow_up_questions': ['如何计算冲量?', '动能和势能是什么?']
                }
            else:
                # 普通对话
                return self.mock_dialogue_response
                
        mock_client_instance.dialogue_with_student_sync.side_effect = dialogue_side_effect
        mock_client_instance.generate_exercises_sync.return_value = self.mock_exercises_response
        
        # 步骤1: 通过对话请求生成练习题
        session_id = str(uuid.uuid4())
        dialogue_data = {
            'query': '请为我生成一些关于牛顿第二定律的练习题',
            'session_id': session_id
        }
        
        dialogue_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(dialogue_data),
            content_type='application/json'
        )
        
        # 验证对话响应
        self.assertEqual(dialogue_response.status_code, status.HTTP_200_OK)
        self.assertTrue(dialogue_response.data['success'])
        self.assertIn('生成', dialogue_response.data['data']['answer'])
        
        # 检查是否包含练习题生成请求信息
        self.assertIn('exercise_request', dialogue_response.data['data'])
        
        # 步骤2: 使用对话中的信息生成练习题
        exercise_request = dialogue_response.data['data']['exercise_request']
        exercise_data = {
            'query': '牛顿第二定律练习题',
            'knowledge_point_ids': exercise_request['knowledge_point_ids'],
            'quantity': exercise_request['quantity'],
            'difficulty': exercise_request['difficulty'],
            'session_id': session_id
        }
        
        exercise_response = self.client.post(
            self.exercise_url,
            data=json.dumps(exercise_data),
            content_type='application/json'
        )
        
        # 验证练习题响应
        self.assertEqual(exercise_response.status_code, status.HTTP_200_OK)
        self.assertTrue(exercise_response.data['success'])
        
        # 步骤3: 继续对话讨论练习题答案
        answer_discussion_data = {
            'query': '请解释一下这道题的答案',
            'session_id': session_id
        }
        
        discussion_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(answer_discussion_data),
            content_type='application/json'
        )
        
        # 验证答案讨论响应
        self.assertEqual(discussion_response.status_code, status.HTTP_200_OK)
        self.assertTrue(discussion_response.data['success'])
        self.assertIn('牛顿第二定律', discussion_response.data['data']['answer'])

    @patch('ai_services.views.N8nWebhookClient')
    def test_error_handling(self, mock_client_class):
        """测试各种错误情况的处理"""
        # 设置模拟客户端
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        # 测试场景1: N8n服务暂时不可用
        mock_client_instance.dialogue_with_student_sync.side_effect = N8nWebhookError("服务不可用")
        
        # 发送请求
        data = {
            'query': '什么是牛顿第二定律?'
        }
        
        response = self.client.post(
            self.dialogue_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], "N8N_WEBHOOK_ERROR")
        
        # 恢复正常行为
        mock_client_instance.dialogue_with_student_sync.side_effect = None
        mock_client_instance.dialogue_with_student_sync.return_value = self.mock_dialogue_response
        
        # 测试场景2: 提供不完整或无效的请求数据
        invalid_data = {'query': ''}  # 空查询
        
        invalid_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 验证无效数据错误响应
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(invalid_response.data['success'])
        
        # 测试场景3: 练习题ID不存在的情况
        correction_data = {
            'exercise_id': 9999,  # 不存在的ID
            'student_answer': '2 m/s^2',
            'session_id': str(uuid.uuid4())
        }
        
        invalid_exercise_response = self.client.post(
            self.correction_url,
            data=json.dumps(correction_data),
            content_type='application/json'
        )
        
        # 验证不存在的练习题错误响应
        self.assertEqual(invalid_exercise_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(invalid_exercise_response.data['success'])
        
        # 测试场景4: 提交非常长的对话内容
        long_query = "牛顿第二定律是什么?" * 500  # 创建一个非常长的查询
        long_data = {
            'query': long_query,
            'session_id': str(uuid.uuid4())
        }
        
        long_query_response = self.client.post(
            self.dialogue_url,
            data=json.dumps(long_data),
            content_type='application/json'
        )
        
        # 验证长查询响应 - 可能返回400错误或成功处理
        if long_query_response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertFalse(long_query_response.data['success'])
        else:
            self.assertEqual(long_query_response.status_code, status.HTTP_200_OK)
            self.assertTrue(long_query_response.data['success'])


class StudentAssistantEndToEndScenarioTests(TestCase):
    """学生助手模块端到端场景测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 与上面集成测试类似的设置
        self.client = APIClient()
        
        # API端点
        self.dialogue_url = reverse('student-dialogue-list')
        self.exercise_url = reverse('ai_services:generate-exercises-list')
        self.correction_url = reverse('ai_services:correct-answer-list')
        
        # 创建测试课程和知识点
        self.teacher = User.objects.create_user(username='teacher2', password='password123')
        self.course = Course.objects.create(
            title="物理学基础", 
            description="高中物理基础课程",
            subject="物理",
            grade_level="高中",
            teacher=self.teacher
        )
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="牛顿运动定律",
            content="牛顿运动定律是经典力学的基础，包括三个定律...",
            importance=5
        )
        
        self.exercise = Exercise.objects.create(
            title="牛顿第二定律应用题",
            content="一个5kg的物体在10N力的作用下，其加速度是多少?",
            type="short_answer",
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template="2 m/s^2"
        )
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_learning_tutorial_scenario(self, mock_client_class):
        """测试学习辅导场景"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # 配置模拟响应序列
        mock_client.dialogue_with_student_sync.side_effect = [
            # 第一次对话响应：解释牛顿第二定律
            {
                'answer': '牛顿第二定律指出，物体的加速度等于作用在它上面的力除以它的质量(a = F/m)。',
                'resources': [{'title': '牛顿运动定律', 'content': '基础知识', 'type': '知识点', 'id': 1}],
                'follow_up_questions': ['什么是牛顿第三定律？', '惯性是什么？']
            },
            # 第二次对话响应：回复学生关于练习题的请求
            {
                'answer': '好的，我已经为你准备了一些练习题，可以帮助你理解牛顿第二定律。',
                'resources': [],
                'follow_up_questions': [],
                'exercise_request': {'knowledge_point_ids': [self.knowledge_point.id], 'quantity': 1}
            },
            # 第三次对话响应：对学生答案的反馈
            {
                'answer': '很好！你的答案是正确的。2 m/s^2是根据牛顿第二定律(F = ma)计算得出的。',
                'resources': [{'title': '力学计算', 'content': '计算方法', 'type': '知识点', 'id': 2}],
                'follow_up_questions': ['如何处理多个力的情况？', '摩擦力如何影响加速度计算？']
            }
        ]
        
        mock_client.generate_exercises_sync.return_value = {
            "questions": [
                {
                    "title": "牛顿第二定律计算题",
                    "content": "一个10kg的物体受到20N的力，求加速度。",
                    "type": "short_answer",
                    "difficulty": 3,
                    "answer_template": "2 m/s^2",
                    "knowledge_point_id": self.knowledge_point.id
                }
            ],
            "session_id": "learning-session"
        }
        
        mock_client.correct_student_answer_sync.return_value = {
            "is_correct": True,
            "score": 100,
            "feedback": "回答正确！",
            "improvement_suggestions": "可以尝试更复杂的问题",
            "explanation": "根据F=ma，a=F/m=20N/10kg=2 m/s^2"
        }
        
        # 创建会话ID
        session_id = "learning-session"
        
        # 步骤1: 学生询问概念
        response1 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '请解释牛顿第二定律', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('牛顿第二定律', response1.data['data']['answer'])
        
        # 步骤2: 学生请求练习题
        response2 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '能给我一些练习题来练习吗?', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIn('exercise_request', response2.data['data'])
        
        # 步骤3: 系统生成练习题
        exercise_data = {
            'query': '牛顿第二定律练习题',
            'knowledge_point_ids': response2.data['data']['exercise_request']['knowledge_point_ids'],
            'session_id': session_id
        }
        response3 = self.client.post(
            self.exercise_url,
            data=json.dumps(exercise_data),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        exercise_id = self.exercise.id  # 使用预设的练习题ID
        
        # 步骤4: 学生提交答案
        response4 = self.client.post(
            self.correction_url,
            data=json.dumps({
                'exercise_id': exercise_id,
                'student_answer': '2 m/s^2',
                'session_id': session_id
            }),
            content_type='application/json'
        )
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
        self.assertTrue(response4.data['data']['is_correct'])
        
        # 步骤5: 学生请求更多解释
        response5 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '你能详细解释一下答案吗?', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response5.status_code, status.HTTP_200_OK)
        self.assertIn('正确', response5.data['data']['answer'])
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_problem_solving_scenario(self, mock_client_class):
        """测试问题解答场景"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # 配置模拟响应序列
        mock_client.dialogue_with_student_sync.side_effect = [
            # 第一次对话响应：如何解二次方程
            {
                'answer': '解二次方程ax^2+bx+c=0可以使用公式法：x = (-b ± √(b^2-4ac)) / 2a。例如，对于方程x^2+5x+6=0，我们有a=1, b=5, c=6...',
                'resources': [{'title': '代数基础', 'content': '二次方程', 'type': '知识点', 'id': 3}],
                'follow_up_questions': ['什么情况下方程没有实数解？', '如何用配方法解二次方程？']
            },
            # 第二次对话响应：回答后续问题
            {
                'answer': '当判别式b^2-4ac小于0时，二次方程没有实数解，只有复数解。例如，方程x^2+2x+5=0的判别式为2^2-4*1*5=4-20=-16<0，所以没有实数解。',
                'resources': [{'title': '复数', 'content': '复数解', 'type': '知识点', 'id': 4}],
                'follow_up_questions': ['复数有什么物理意义？', '如何求复数解？']
            }
        ]
        
        # 创建会话ID
        session_id = "problem-session"
        
        # 步骤1: 学生提出问题
        response1 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '如何解二次方程？', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('二次方程', response1.data['data']['answer'])
        self.assertIn('follow_up_questions', response1.data['data'])
        
        # 步骤2: 学生提出后续问题
        response2 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '什么情况下方程没有实数解？', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIn('判别式', response2.data['data']['answer'])
        
        # 验证会话ID保持一致
        self.assertEqual(response1.data['data']['session_id'], session_id)
        self.assertEqual(response2.data['data']['session_id'], session_id)
        
    @patch('ai_services.views.N8nWebhookClient')
    def test_multi_topic_scenario(self, mock_client_class):
        """测试多主题学习场景"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # 配置模拟响应序列
        mock_client.dialogue_with_student_sync.side_effect = [
            # 物理话题响应
            {
                'answer': '牛顿第二定律指出，物体的加速度等于作用在它上面的力除以它的质量(a = F/m)。',
                'resources': [{'title': '物理力学', 'content': '力学基础', 'type': '知识点', 'id': 5}],
                'follow_up_questions': []
            },
            # 化学话题响应
            {
                'answer': '水的化学式是H₂O，表示每个水分子由两个氢原子和一个氧原子组成。',
                'resources': [{'title': '化学基础', 'content': '分子结构', 'type': '知识点', 'id': 6}],
                'follow_up_questions': []
            },
            # 数学话题响应
            {
                'answer': '微积分是数学的一个分支，主要研究函数、极限、微分、积分和无穷级数。它由牛顿和莱布尼茨独立发明。',
                'resources': [{'title': '高等数学', 'content': '微积分基础', 'type': '知识点', 'id': 7}],
                'follow_up_questions': []
            }
        ]
        
        # 创建会话ID
        session_id = "multi-topic-session"
        
        # 步骤1: 物理话题
        response1 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '什么是牛顿第二定律？', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('牛顿第二定律', response1.data['data']['answer'])
        
        # 步骤2: 切换到化学话题
        response2 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '水的化学式是什么？', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIn('H₂O', response2.data['data']['answer'])
        
        # 步骤3: 切换到数学话题
        response3 = self.client.post(
            self.dialogue_url,
            data=json.dumps({'query': '微积分是什么？', 'session_id': session_id}),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertIn('微积分', response3.data['data']['answer'])
        
        # 验证会话ID保持一致
        self.assertEqual(response1.data['data']['session_id'], session_id)
        self.assertEqual(response2.data['data']['session_id'], session_id)
        self.assertEqual(response3.data['data']['session_id'], session_id) 