import os
import shutil
import tempfile
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage

from courses.models import Course, KnowledgePoint
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService
from marp_service import convert_markdown_to_format

User = get_user_model()


class KnowledgePointToPPTIntegrationTests(TestCase):
    """测试知识点到PPT转换的完整流程"""
    
    def setUp(self):
        # 创建测试用户
        self.teacher = User.objects.create_user(
            username='test_teacher',
            email='teacher@example.com',
            password='password123'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title="Python编程基础",
            subject="计算机科学",
            grade_level="大学一年级",
            teacher=self.teacher
        )
        
        # 创建测试知识点及层次结构
        self.kp1 = KnowledgePoint.objects.create(
            title="Python基础概念",
            content="Python是一种高级编程语言，以简单易学著称。",
            course=self.course,
            importance=5
        )
        
        self.kp2 = KnowledgePoint.objects.create(
            title="变量与数据类型",
            content="Python中的变量不需要声明类型，常见数据类型包括整数、浮点数、字符串、列表等。",
            course=self.course,
            parent=self.kp1,
            importance=4
        )
        
        self.kp3 = KnowledgePoint.objects.create(
            title="控制流语句",
            content="Python支持if-else条件语句、for和while循环等控制流结构。",
            course=self.course,
            parent=self.kp1,
            importance=4
        )
        
        # 创建服务实例
        self.service = KnowledgePointToPPTService()
        
        # 创建临时目录用于测试
        self.test_media_root = tempfile.mkdtemp()
        
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())  # 使用临时目录而非None
    def test_fetch_knowledge_points_hierarchy(self):
        """测试获取知识点层次结构"""
        # 获取知识点层次结构
        hierarchy = self.service.fetch_knowledge_points_hierarchy(
            knowledge_point_ids=[self.kp1.id],
            include_children=True,
            max_depth=3
        )
        
        # 验证结构
        self.assertIn("knowledge_points", hierarchy)
        self.assertIn("courses", hierarchy)
        self.assertEqual(len(hierarchy["knowledge_points"]), 1)
        self.assertEqual(hierarchy["knowledge_points"][0]["id"], self.kp1.id)
        self.assertEqual(hierarchy["knowledge_points"][0]["title"], "Python基础概念")
        
        # 验证子知识点
        self.assertIn("children", hierarchy["knowledge_points"][0])
        children = hierarchy["knowledge_points"][0]["children"]
        self.assertEqual(len(children), 2)
        
        # 验证课程信息
        self.assertEqual(len(hierarchy["courses"]), 1)
        # 修复：直接使用整数ID而不是字符串
        self.assertIn(self.course.id, hierarchy["courses"])
        self.assertEqual(hierarchy["courses"][self.course.id]["title"], "Python编程基础")
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())  # 使用临时目录而非None
    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')  # 修改为正确的导入路径
    def test_generate_markdown_and_convert_to_ppt(self, mock_convert):
        """测试生成Markdown并转换为PPT的流程"""
        # 模拟转换函数
        mock_convert.return_value = "/tmp/test_output.pptx"
        
        # 获取知识点层次结构
        hierarchy = self.service.fetch_knowledge_points_hierarchy(
            knowledge_point_ids=[self.kp1.id],
            include_children=True,
            max_depth=2
        )
        
        # 生成Markdown
        markdown = self.service.generate_markdown_from_knowledge_points(
            hierarchy,
            title="Python编程概念",
            include_course_info=True
        )
        
        # 验证Markdown内容
        self.assertIn("marp: true", markdown)
        self.assertIn("# Python编程概念", markdown)
        self.assertIn("Python基础概念", markdown)
        self.assertIn("变量与数据类型", markdown)
        self.assertIn("控制流语句", markdown)
        
        # 转换为PPT
        output_path, filename = self.service.validate_and_convert_markdown(
            markdown,
            format='pptx',
            theme='default'
        )
        
        # 验证转换调用
        mock_convert.assert_called_once()
        args, kwargs = mock_convert.call_args
        self.assertEqual(kwargs["content"], markdown)
        self.assertEqual(kwargs["output_format"], "pptx")
        self.assertEqual(kwargs["theme"], "default")
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())  # 使用临时目录而非None
    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')
    def test_process_knowledge_points_to_ppt(self, mock_convert):
        """测试完整的知识点到PPT流程"""
        # 模拟转换函数
        mock_convert.return_value = "/tmp/test_output.pptx"
        
        # 构造输入数据
        data = {
            "knowledge_point_ids": [self.kp1.id],
            "include_children": True,
            "max_depth": 2,
            "format": "pptx",
            "theme": "default",
            "title": "Python编程概念",
            "include_course_info": True,
            "use_ai": False
        }
        
        # 处理知识点到PPT
        result = self.service.process_knowledge_points_to_ppt(data)
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("file_url", result["data"])
        self.assertIn("filename", result["data"])
        self.assertTrue(result["data"]["filename"].endswith(".pptx"))
        
        # 验证转换调用
        mock_convert.assert_called_once() 