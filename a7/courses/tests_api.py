from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Course, KnowledgePoint
from users.models import User, Role
import json

class CourseAPITests(TestCase):
    """测试课程API的功能"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建一个角色 
        self.admin_role = Role.objects.create(name='admin', description='管理员角色')
        self.teacher_role = Role.objects.create(name='teacher', description='教师角色')
        self.student_role = Role.objects.create(name='student', description='学生角色')
        
        # 创建测试用户
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='adminpass',
            role='admin',
            is_staff=True
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher', 
            email='teacher@example.com', 
            password='teacherpass',
            role='teacher'
        )
        
        self.student_user = User.objects.create_user(
            username='student', 
            email='student@example.com', 
            password='studentpass',
            role='student'
        )
        
        # 创建一个测试课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='计算机科学',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 初始化API客户端
        self.client = APIClient()
    
    def test_list_courses(self):
        """测试获取课程列表"""
        # 1. 未认证用户无法访问
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 认证用户可以访问
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 验证课程数据
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], '测试课程')
    
    def test_retrieve_course(self):
        """测试获取单个课程"""
        # 认证用户可以获取课程详情
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        
        # 验证课程数据
        course_data = response.data['data']
        self.assertEqual(course_data['title'], '测试课程')
        self.assertEqual(course_data['subject'], '计算机科学')
    
    def test_create_course(self):
        """测试创建课程"""
        url = reverse('course-list')
        data = {
            'title': '新课程',
            'description': '这是一个新课程',
            'subject': '数学',
            'grade_level': '初中'
        }
        
        # 1. 未认证用户无法创建
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 学生无法创建课程
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 教师可以创建课程
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的课程
        self.assertEqual(Course.objects.count(), 2)
        new_course = Course.objects.get(title='新课程')
        self.assertEqual(new_course.subject, '数学')
        self.assertEqual(new_course.teacher, self.teacher_user)
        
        # 4. 管理员也可以创建课程
        data['title'] = '管理员课程'
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的课程
        self.assertEqual(Course.objects.count(), 3)
    
    def test_update_course(self):
        """测试更新课程"""
        url = reverse('course-detail', args=[self.course.id])
        data = {
            'title': '更新后的课程',
            'description': '这是更新后的描述',
            'subject': '计算机科学',
            'grade_level': '高中'
        }
        
        # 1. 学生无法更新课程
        self.client.force_authenticate(user=self.student_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. 其他教师无法更新课程
        another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        self.client.force_authenticate(user=another_teacher)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 课程创建者可以更新课程
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新后的课程
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, '更新后的课程')
        self.assertEqual(self.course.description, '这是更新后的描述')
        
        # 4. 管理员可以更新任何课程
        data['title'] = '管理员更新的课程'
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新后的课程
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, '管理员更新的课程')
    
    def test_delete_course(self):
        """测试删除课程"""
        url = reverse('course-detail', args=[self.course.id])
        
        # 1. 学生无法删除课程
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. 其他教师无法删除课程
        another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        self.client.force_authenticate(user=another_teacher)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 创建更多测试课程
        course2 = Course.objects.create(
            title='测试课程2',
            description='这是第二个测试课程',
            subject='物理',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 4. 课程创建者可以删除课程
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(reverse('course-detail', args=[course2.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证课程已删除
        self.assertEqual(Course.objects.filter(id=course2.id).count(), 0)
        
        # 5. 管理员可以删除任何课程
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证课程已删除
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 0)
    
    def test_my_courses(self):
        """测试获取当前用户创建的课程列表"""
        # 教师创建多个课程
        Course.objects.create(
            title='教师课程1',
            description='这是教师的第一个课程',
            subject='语文',
            grade_level='初中',
            teacher=self.teacher_user
        )
        Course.objects.create(
            title='教师课程2',
            description='这是教师的第二个课程',
            subject='英语',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        # 另一个教师创建课程
        another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        Course.objects.create(
            title='另一个教师的课程',
            description='这是另一个教师的课程',
            subject='历史',
            grade_level='高中',
            teacher=another_teacher
        )
        
        # 测试获取自己的课程列表
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(reverse('course-my-courses'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 验证课程数据
        results = response.data['data']['results']
        self.assertEqual(len(results), 3)
        
        # 验证返回的课程标题
        titles = [item['title'] for item in results]
        self.assertIn('测试课程', titles)
        self.assertIn('教师课程1', titles)
        self.assertIn('教师课程2', titles)
        self.assertNotIn('另一个教师的课程', titles)


class KnowledgePointAPITests(TestCase):
    """测试知识点API的功能"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建角色
        self.admin_role = Role.objects.create(name='admin', description='管理员角色')
        self.teacher_role = Role.objects.create(name='teacher', description='教师角色')
        self.student_role = Role.objects.create(name='student', description='学生角色')
        
        # 创建用户
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='adminpass',
            role='admin',
            is_staff=True
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher', 
            email='teacher@example.com', 
            password='teacherpass',
            role='teacher'
        )
        
        self.another_teacher = User.objects.create_user(
            username='teacher2', 
            email='teacher2@example.com', 
            password='teacher2pass',
            role='teacher'
        )
        
        self.student_user = User.objects.create_user(
            username='student', 
            email='student@example.com', 
            password='studentpass',
            role='student'
        )
        
        # 创建课程
        self.course = Course.objects.create(
            title='测试课程',
            description='这是一个测试课程',
            subject='计算机科学',
            grade_level='高中',
            teacher=self.teacher_user
        )
        
        self.another_course = Course.objects.create(
            title='另一个课程',
            description='这是另一个测试课程',
            subject='数学',
            grade_level='初中',
            teacher=self.another_teacher
        )
        
        # 创建知识点
        self.parent_kp = KnowledgePoint.objects.create(
            title='父知识点',
            content='这是一个父知识点',
            importance=8,
            course=self.course
        )
        
        self.child_kp = KnowledgePoint.objects.create(
            title='子知识点',
            content='这是一个子知识点',
            importance=5,
            course=self.course,
            parent=self.parent_kp
        )
        
        self.another_kp = KnowledgePoint.objects.create(
            title='另一个知识点',
            content='这是另一个课程的知识点',
            importance=7,
            course=self.another_course
        )
        
        # 初始化API客户端
        self.client = APIClient()
        
    def test_list_knowledge_points(self):
        """测试获取知识点列表"""
        # 1. 未认证用户无法访问
        response = self.client.get(reverse('knowledge-point-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 认证用户可以访问
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('knowledge-point-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 验证知识点数据
        results = response.data['data']['results']
        self.assertEqual(len(results), 3)  # 应该有3个知识点
        
        # 3. 测试按课程过滤
        response = self.client.get(reverse('knowledge-point-list'), {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 2)  # 第一个课程有2个知识点
        
        response = self.client.get(reverse('knowledge-point-list'), {'course': self.another_course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)  # 第二个课程有1个知识点
        
        # 4. 测试按父知识点过滤
        response = self.client.get(reverse('knowledge-point-list'), {'parent': self.parent_kp.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)  # 父知识点有1个子知识点
        self.assertEqual(results[0]['title'], '子知识点')
        
        # 5. 测试获取顶级知识点
        response = self.client.get(reverse('knowledge-point-list'), {'parent': 'null'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 2)  # 有2个顶级知识点
    
    def test_retrieve_knowledge_point(self):
        """测试获取单个知识点"""
        # 认证用户可以获取知识点详情
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('knowledge-point-detail', args=[self.parent_kp.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        
        # 验证知识点数据
        kp_data = response.data['data']
        self.assertEqual(kp_data['title'], '父知识点')
        self.assertEqual(kp_data['importance'], 8)
        self.assertEqual(kp_data['course'], self.course.id)
        self.assertEqual(kp_data['course_title'], '测试课程')
        self.assertIsNone(kp_data['parent'])
        
        # 验证子知识点信息
        children = kp_data['children']
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]['title'], '子知识点')
    
    def test_create_knowledge_point(self):
        """测试创建知识点"""
        url = reverse('knowledge-point-list')
        data = {
            'title': '新知识点',
            'content': '这是一个新的知识点',
            'importance': 6,
            'course': self.course.id
        }
        
        # 1. 未认证用户无法创建
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 学生无法创建知识点
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 教师可以创建知识点
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的知识点
        self.assertEqual(KnowledgePoint.objects.count(), 4)  # 现在有4个知识点
        new_kp = KnowledgePoint.objects.get(title='新知识点')
        self.assertEqual(new_kp.importance, 6)
        self.assertEqual(new_kp.course.id, self.course.id)
        
        # 4. 创建带父级的知识点
        data = {
            'title': '另一个子知识点',
            'content': '这是父知识点的另一个子知识点',
            'importance': 4,
            'course': self.course.id,
            'parent': self.parent_kp.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的子知识点
        self.assertEqual(KnowledgePoint.objects.count(), 5)  # 现在有5个知识点
        child_kp = KnowledgePoint.objects.get(title='另一个子知识点')
        self.assertEqual(child_kp.parent.id, self.parent_kp.id)
        
        # 5. 尝试创建父子知识点不属于同一课程的情况
        data = {
            'title': '错误的子知识点',
            'content': '这个知识点的父级属于另一个课程',
            'importance': 3,
            'course': self.another_course.id,
            'parent': self.parent_kp.id  # 父级属于self.course
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 确认知识点数量没有增加
        self.assertEqual(KnowledgePoint.objects.count(), 5)
    
    def test_update_knowledge_point(self):
        """测试更新知识点"""
        url = reverse('knowledge-point-detail', args=[self.child_kp.id])
        data = {
            'title': '更新后的子知识点',
            'content': '这是更新后的子知识点内容',
            'importance': 7
        }
        
        # 1. 学生无法更新知识点
        self.client.force_authenticate(user=self.student_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. 非课程教师无法更新知识点
        self.client.force_authenticate(user=self.another_teacher)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 课程教师可以更新知识点
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新后的知识点
        self.child_kp.refresh_from_db()
        self.assertEqual(self.child_kp.title, '更新后的子知识点')
        self.assertEqual(self.child_kp.importance, 7)
        
        # 4. 管理员可以更新任何知识点
        data['title'] = '管理员更新的子知识点'
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新后的知识点
        self.child_kp.refresh_from_db()
        self.assertEqual(self.child_kp.title, '管理员更新的子知识点')
        
        # 5. 测试循环引用检测 - 尝试将父知识点的parent设为子知识点
        url = reverse('knowledge-point-detail', args=[self.parent_kp.id])
        data = {
            'title': self.parent_kp.title,
            'content': self.parent_kp.content,
            'importance': self.parent_kp.importance,
            'parent': self.child_kp.id  # 尝试将子知识点设为父知识点的父级
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_knowledge_point(self):
        """测试删除知识点"""
        url = reverse('knowledge-point-detail', args=[self.parent_kp.id])
        
        # 1. 学生无法删除知识点
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. 非课程教师无法删除知识点
        self.client.force_authenticate(user=self.another_teacher)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. 创建额外的知识点用于测试
        extra_kp = KnowledgePoint.objects.create(
            title='额外知识点',
            content='这是一个额外的测试知识点',
            importance=3,
            course=self.course
        )
        
        # 4. 课程教师可以删除知识点
        self.client.force_authenticate(user=self.teacher_user)
        extra_url = reverse('knowledge-point-detail', args=[extra_kp.id])
        response = self.client.delete(extra_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证知识点已删除
        self.assertEqual(KnowledgePoint.objects.filter(id=extra_kp.id).count(), 0)
        
        # 5. 测试删除父知识点会级联删除子知识点
        parent_id = self.parent_kp.id
        child_id = self.child_kp.id
        
        # 记录原始知识点数量
        original_count = KnowledgePoint.objects.count()
        
        # 管理员删除父知识点
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证父知识点和子知识点都已删除
        self.assertEqual(KnowledgePoint.objects.count(), original_count - 2)
        self.assertEqual(KnowledgePoint.objects.filter(id=parent_id).count(), 0)
        self.assertEqual(KnowledgePoint.objects.filter(id=child_id).count(), 0)
    
    def test_top_level_knowledge_points(self):
        """测试获取顶级知识点"""
        # 添加更多的顶级知识点
        KnowledgePoint.objects.create(
            title='课程1的顶级知识点2',
            content='这是课程1的另一个顶级知识点',
            importance=4,
            course=self.course
        )
        
        KnowledgePoint.objects.create(
            title='课程2的顶级知识点2',
            content='这是课程2的另一个顶级知识点',
            importance=6,
            course=self.another_course
        )
        
        # 认证用户访问顶级知识点接口
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('knowledge-point-top-level'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 应该有4个顶级知识点
        results = response.data['data']['results']
        self.assertEqual(len(results), 4)
        
        # 测试按课程筛选顶级知识点
        response = self.client.get(
            reverse('knowledge-point-top-level'), 
            {'course': self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 2)  # 第一个课程有2个顶级知识点
        
        response = self.client.get(
            reverse('knowledge-point-top-level'), 
            {'course': self.another_course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 2)  # 第二个课程有2个顶级知识点
    
    def test_children_knowledge_points(self):
        """测试获取子知识点"""
        # 为父知识点添加更多子知识点
        KnowledgePoint.objects.create(
            title='子知识点2',
            content='这是第二个子知识点',
            importance=4,
            course=self.course,
            parent=self.parent_kp
        )
        
        KnowledgePoint.objects.create(
            title='子知识点3',
            content='这是第三个子知识点',
            importance=3,
            course=self.course,
            parent=self.parent_kp
        )
        
        # 认证用户访问子知识点接口
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(
            reverse('knowledge-point-children', args=[self.parent_kp.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应结构和数据
        self.assertTrue('success' in response.data)
        self.assertTrue(response.data['success'])
        self.assertTrue('data' in response.data)
        self.assertTrue('results' in response.data['data'])
        
        # 父知识点应该有3个子知识点
        results = response.data['data']['results']
        self.assertEqual(len(results), 3)
        
        # 验证子知识点排序（按importance降序和title排序）
        self.assertEqual(results[0]['importance'], 5)  # self.child_kp的importance是5
        self.assertEqual(results[1]['importance'], 4)
        self.assertEqual(results[2]['importance'], 3) 