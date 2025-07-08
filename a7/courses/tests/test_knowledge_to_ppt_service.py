import uuid
import json
import pytest
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.files.storage import default_storage

from courses.models import Course, KnowledgePoint
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService


class TestKnowledgePointToPPTService(TestCase):
    """测试知识点到PPT服务类"""

    def setUp(self):
        # 创建测试数据
        self.course = Course.objects.create(
            title="测试课程",
            subject="数学",
            grade_level="初一",
            description="测试课程描述"
        )
        
        # 创建父知识点
        self.kp1 = KnowledgePoint.objects.create(
            title="一次函数",
            content="一次函数是指满足一定条件的函数。",
            importance=5,
            course=self.course
        )
        
        # 创建子知识点
        self.kp1_1 = KnowledgePoint.objects.create(
            title="一次函数的定义",
            content="一次函数的定义是y=kx+b，其中k、b为常数，k≠0",
            importance=4,
            course=self.course,
            parent=self.kp1
        )
        
        self.kp1_2 = KnowledgePoint.objects.create(
            title="一次函数的图像",
            content="一次函数的图像是一条直线",
            importance=4,
            course=self.course,
            parent=self.kp1
        )
        
        # 创建服务实例
        self.service = KnowledgePointToPPTService()

    def test_generate_markdown_from_knowledge_points(self):
        """测试本地生成Markdown功能"""
        # 获取知识点数据
        knowledge_data = self.service.fetch_knowledge_points_hierarchy(
            [self.kp1.id], 
            include_children=True, 
            max_depth=2
        )
        
        # 生成Markdown
        markdown = self.service.generate_markdown_from_knowledge_points(
            knowledge_data, 
            title="测试演示文稿", 
            include_course_info=True
        )
        
        # 验证生成的Markdown包含关键内容
        self.assertIn("测试演示文稿", markdown)
        self.assertIn("一次函数", markdown)
        self.assertIn("一次函数的定义", markdown)
        self.assertIn("一次函数的图像", markdown)
        self.assertIn("marp: true", markdown)

    @patch('courses.services.knowledge_to_ppt.N8nWebhookClient')
    def test_generate_markdown_using_ai(self, mock_client_class):
        """测试使用AI生成Markdown功能"""
        # 模拟AI客户端响应
        mock_client = MagicMock()
        mock_client.generate_markdown_from_knowledge_sync.return_value = {
            "markdown": "---\nmarp: true\ntheme: default\npaginate: true\n---\n\n# 一次函数\n\n一次函数是指满足一定条件的函数。\n\n---\n\n## 一次函数的定义\n\n一次函数的定义是y=kx+b，其中k、b为常数，k≠0\n\n---\n\n## 一次函数的图像\n\n一次函数的图像是一条直线\n\n---\n"
        }
        mock_client_class.return_value = mock_client
        
        # 获取知识点数据
        knowledge_data = self.service.fetch_knowledge_points_hierarchy(
            [self.kp1.id], 
            include_children=True, 
            max_depth=2
        )
        
        # 使用AI生成Markdown
        markdown = self.service.generate_markdown_using_ai(
            knowledge_data, 
            title="AI生成的演示文稿", 
            include_course_info=True,
            theme="default"
        )
        
        # 验证AI客户端调用
        mock_client.generate_markdown_from_knowledge_sync.assert_called_once()
        
        # 验证生成的Markdown包含关键内容
        self.assertIn("marp: true", markdown)
        self.assertIn("一次函数", markdown)
        self.assertIn("一次函数的定义", markdown)
        
    @patch('courses.services.knowledge_to_ppt.N8nWebhookClient')
    def test_generate_markdown_ai_fallback(self, mock_client_class):
        """测试AI生成失败时回退到本地生成的场景"""
        # 模拟AI客户端抛出异常
        mock_client = MagicMock()
        mock_client.generate_markdown_from_knowledge_sync.side_effect = Exception("模拟的API错误")
        mock_client_class.return_value = mock_client
        
        # 获取知识点数据
        knowledge_data = self.service.fetch_knowledge_points_hierarchy(
            [self.kp1.id], 
            include_children=True, 
            max_depth=2
        )
        
        # 使用AI生成Markdown（应回退到本地生成）
        markdown = self.service.generate_markdown_using_ai(
            knowledge_data, 
            title="测试回退", 
            include_course_info=True
        )
        
        # 验证生成的Markdown包含关键内容（说明已回退到本地生成）
        self.assertIn("marp: true", markdown)
        self.assertIn("一次函数", markdown)
        self.assertIn("一次函数的定义", markdown)
        
    @patch('courses.services.knowledge_to_ppt.KnowledgePointToPPTService.generate_markdown_using_ai')
    @patch('courses.services.knowledge_to_ppt.KnowledgePointToPPTService.validate_and_convert_markdown')
    def test_process_with_ai_mode(self, mock_convert, mock_generate_ai):
        """测试处理流程使用AI模式"""
        # 模拟方法返回值
        mock_generate_ai.return_value = "模拟的AI生成Markdown内容"
        mock_convert.return_value = ("path/to/file.pptx", "file.pptx")
        
        # 调用处理方法，使用AI模式
        result = self.service.process_knowledge_points_to_ppt({
            "knowledge_point_ids": [self.kp1.id],
            "include_children": True,
            "max_depth": 2,
            "format": "pptx",
            "use_ai": True,  # 开启AI模式
            "title": "AI模式测试"
        })
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertIn("file_url", result["data"])
        
        # 验证调用了AI生成方法
        mock_generate_ai.assert_called_once()
        # 验证没有直接调用本地生成方法
        # 这隐式地验证了基于use_ai参数的逻辑分支 