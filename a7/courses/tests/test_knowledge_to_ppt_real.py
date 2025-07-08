import os
import shutil
import unittest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from courses.models import Course, KnowledgePoint
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService

User = get_user_model()

# 创建测试媒体目录
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'test_media')
TEST_PRESENTATION_DIR = os.path.join(TEST_MEDIA_ROOT, 'presentations')

# 检查marp-cli是否在系统PATH中
MARP_CLI_INSTALLED = shutil.which('marp') is not None or shutil.which('npx') is not None

# 如果环境变量中指定跳过集成测试，也会跳过
if os.environ.get('SKIP_MARP_INTEGRATION_TESTS'):
    MARP_CLI_INSTALLED = False


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
@unittest.skipIf(not MARP_CLI_INSTALLED, "Marp CLI未安装或环境变量设置为跳过，跳过集成测试")
class KnowledgePointToPPTRealTests(TestCase):
    """真实测试知识点到PPT转换功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='Python编程基础',
            subject='计算机科学',
            grade_level='大学一年级',
            teacher=self.user
        )
        
        # 创建父知识点
        self.kp_python = KnowledgePoint.objects.create(
            title='Python编程语言',
            content='Python是一种高级编程语言，以其简洁、易读的语法著称。它支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。',
            course=self.course,
            importance=5
        )
        
        # 创建子知识点
        self.kp_variables = KnowledgePoint.objects.create(
            title='变量与数据类型',
            content='Python中的变量无需声明类型，可以直接赋值使用。主要数据类型包括：整数(int)、浮点数(float)、字符串(str)、布尔值(bool)、列表(list)、元组(tuple)、字典(dict)和集合(set)。',
            course=self.course,
            parent=self.kp_python,
            importance=4
        )
        
        self.kp_control = KnowledgePoint.objects.create(
            title='控制流',
            content='Python的控制流语句包括if-else条件语句、for和while循环、以及try-except异常处理。\n\n```python\n# 条件语句示例\nif x > 0:\n    print("正数")\nelif x == 0:\n    print("零")\nelse:\n    print("负数")\n```',
            course=self.course,
            parent=self.kp_python,
            importance=4
        )
        
        self.kp_functions = KnowledgePoint.objects.create(
            title='函数定义与调用',
            content='Python函数使用def关键字定义，可以有默认参数、可变参数和关键字参数。\n\n```python\ndef greet(name, greeting="Hello"):\n    return f"{greeting}, {name}!"\n\nprint(greet("世界"))  # 输出: Hello, 世界!\n```',
            course=self.course,
            parent=self.kp_python,
            importance=4
        )
        
        # 创建子知识点的子知识点
        self.kp_lists = KnowledgePoint.objects.create(
            title='列表操作',
            content='列表是Python中最常用的数据结构之一，支持索引、切片、添加、删除等多种操作。\n\n```python\n# 列表操作示例\nfruits = ["苹果", "香蕉", "橙子"]\nfruits.append("葡萄")  # 添加元素\nprint(fruits[1:3])    # 切片: ["香蕉", "橙子"]\n```',
            course=self.course,
            parent=self.kp_variables,
            importance=3
        )
        
        self.kp_dicts = KnowledgePoint.objects.create(
            title='字典操作',
            content='字典是键值对的集合，通过键可以快速访问对应的值。\n\n```python\n# 字典操作示例\nuser = {"name": "张三", "age": 25, "email": "zhang@example.com"}\nprint(user["name"])  # 输出: 张三\nuser["phone"] = "123456789"  # 添加新键值对\n```',
            course=self.course,
            parent=self.kp_variables,
            importance=3
        )
        
        # 创建API客户端
        self.client = APIClient()
        
        # 确保测试媒体目录存在
        os.makedirs(TEST_PRESENTATION_DIR, exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        # 清理测试媒体目录
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)
    
    def test_create_real_pptx(self):
        """测试创建实际的PPTX文件"""
        # 准备请求数据
        request_data = {
            "knowledge_point_ids": [self.kp_python.id],
            "include_children": True,
            "max_depth": 3,
            "format": "pptx",
            "theme": "default",
            "title": "Python编程基础知识"
        }
        
        # 发送请求
        url = reverse('knowledge-points-to-ppt-list')
        response = self.client.post(url, request_data, format='json')
        
        # 打印响应内容，帮助调试
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.data}")
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 检查响应中是否包含文件URL
        self.assertIn("data", response.data)
        self.assertIn("file_url", response.data["data"])
        self.assertIn("filename", response.data["data"])
        
        # 验证文件是否实际存在
        file_path = os.path.join(settings.MEDIA_ROOT, response.data["data"]["file_url"].replace(settings.MEDIA_URL, ""))
        self.assertTrue(os.path.exists(file_path), f"文件不存在: {file_path}")
        
        # 验证文件大小是否合理（PPTX文件应该至少有几KB）
        file_size = os.path.getsize(file_path)
        self.assertGreater(file_size, 1000, f"文件大小过小: {file_size} 字节")
        
        print(f"生成的PPTX文件: {file_path}")
        print(f"文件大小: {file_size} 字节")
        
        # 如果需要，可以将文件复制到更容易访问的位置
        output_dir = os.path.join(settings.BASE_DIR, '..', 'pptx_output')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"python_basics_{self.kp_python.id}.pptx")
        shutil.copy(file_path, output_file)
        print(f"文件已复制到: {os.path.abspath(output_file)}") 