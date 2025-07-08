import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase
from django.conf import settings

from marp_service.validation import MarkdownValidator
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService


class ValidateAndConvertMarkdownTests(TestCase):
    """测试知识点到PPT转换服务的Markdown验证和转换功能"""
    
    def setUp(self):
        # 创建服务实例
        self.service = KnowledgePointToPPTService()
        
        # 模拟有效的Markdown内容
        self.valid_markdown = """---
marp: true
theme: default
paginate: true
---

# 测试标题
这是一个测试幻灯片

---

## 第二页
- 项目1
- 项目2
"""
        
        # 模拟无效的Markdown内容 (缺少前置元数据)
        self.invalid_markdown = """# 测试标题
这是一个测试幻灯片，但缺少前置元数据

---

## 第二页
- 项目1
- 项目2
"""

        # 模拟修复后的Markdown
        self.fixed_markdown = """---
marp: true
theme: default
paginate: true
---

# 测试标题
这是一个测试幻灯片，但缺少前置元数据

---

## 第二页
- 项目1
- 项目2
"""

    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')
    @patch('courses.services.knowledge_to_ppt.uuid.uuid4')
    def test_validate_and_convert_valid_markdown(self, mock_uuid, mock_convert):
        """测试验证和转换有效的Markdown内容"""
        # 设置模拟UUID和转换函数
        mock_uuid.return_value = "test-uuid"
        mock_convert.return_value = "/tmp/test_output.pptx"
        
        # 调用测试方法
        output_path, filename = self.service.validate_and_convert_markdown(
            self.valid_markdown, 
            format='pptx', 
            theme='default'
        )
        
        # 验证结果
        self.assertEqual(filename, "presentation_test-uuid.pptx")
        self.assertTrue(output_path.endswith("presentation_test-uuid.pptx"))
        
        # 验证convert_markdown_to_format调用
        mock_convert.assert_called_once()
        args, kwargs = mock_convert.call_args
        self.assertEqual(kwargs["content"], self.valid_markdown)
        self.assertEqual(kwargs["output_format"], "pptx")
        self.assertEqual(kwargs["theme"], "default")

    @patch('courses.services.knowledge_to_ppt.MarkdownValidator')
    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')
    @patch('courses.services.knowledge_to_ppt.uuid.uuid4')
    def test_validate_and_fix_invalid_markdown(self, mock_uuid, mock_convert, mock_validator_class):
        """测试验证和修复无效的Markdown内容"""
        # 设置模拟UUID和转换函数
        mock_uuid.return_value = "test-uuid"
        mock_convert.return_value = "/tmp/test_output.pptx"
        
        # 设置模拟验证器
        mock_validator = MagicMock()
        mock_validator.validate.return_value = False
        mock_validator.get_issues.return_value = ["Missing frontmatter"]
        mock_validator.fix.return_value = self.fixed_markdown
        
        # 第二个验证器实例（修复后验证）
        mock_validator2 = MagicMock()
        mock_validator2.validate.return_value = True
        
        mock_validator_class.side_effect = [mock_validator, mock_validator2]
        
        # 调用测试方法
        output_path, filename = self.service.validate_and_convert_markdown(
            self.invalid_markdown, 
            format='pptx', 
            theme='default'
        )
        
        # 验证结果
        self.assertEqual(filename, "presentation_test-uuid.pptx")
        self.assertTrue(output_path.endswith("presentation_test-uuid.pptx"))
        
        # 验证验证器和修复被调用
        mock_validator.validate.assert_called_once()
        mock_validator.get_issues.assert_called_once()
        mock_validator.fix.assert_called_once()
        
        # 验证convert_markdown_to_format调用
        mock_convert.assert_called_once()
        args, kwargs = mock_convert.call_args
        self.assertEqual(kwargs["content"], self.fixed_markdown)
        self.assertEqual(kwargs["output_format"], "pptx")
        self.assertEqual(kwargs["theme"], "default")

    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')
    @patch('courses.services.knowledge_to_ppt.uuid.uuid4')
    def test_different_output_formats(self, mock_uuid, mock_convert):
        """测试不同的输出格式"""
        # 设置模拟UUID和转换函数
        mock_uuid.return_value = "test-uuid"
        mock_convert.return_value = "/tmp/test_output.pdf"
        
        formats = ["pdf", "html", "pptx"]
        
        for format in formats:
            # 重置模拟
            mock_convert.reset_mock()
            
            # 调用测试方法
            output_path, filename = self.service.validate_and_convert_markdown(
                self.valid_markdown, 
                format=format, 
                theme='default'
            )
            
            # 验证结果
            self.assertEqual(filename, f"presentation_test-uuid.{format}")
            self.assertTrue(output_path.endswith(f"presentation_test-uuid.{format}"))
            
            # 验证convert_markdown_to_format调用
            mock_convert.assert_called_once()
            args, kwargs = mock_convert.call_args
            self.assertEqual(kwargs["output_format"], format)

    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')
    @patch('courses.services.knowledge_to_ppt.uuid.uuid4')
    def test_different_themes(self, mock_uuid, mock_convert):
        """测试不同的主题"""
        # 设置模拟UUID和转换函数
        mock_uuid.return_value = "test-uuid"
        mock_convert.return_value = "/tmp/test_output.pptx"
        
        themes = ["default", "gaia", "uncover"]
        
        for theme in themes:
            # 重置模拟
            mock_convert.reset_mock()
            
            # 调用测试方法
            output_path, filename = self.service.validate_and_convert_markdown(
                self.valid_markdown, 
                format='pptx', 
                theme=theme
            )
            
            # 验证结果
            self.assertEqual(filename, "presentation_test-uuid.pptx")
            
            # 验证convert_markdown_to_format调用
            mock_convert.assert_called_once()
            args, kwargs = mock_convert.call_args
            self.assertEqual(kwargs["theme"], theme)

    @patch('courses.services.knowledge_to_ppt.convert_markdown_to_format')
    @patch('courses.services.knowledge_to_ppt.logger')
    def test_conversion_exception_handling(self, mock_logger, mock_convert):
        """测试转换异常处理"""
        # 设置模拟转换函数抛出异常
        error_msg = "测试转换错误"
        mock_convert.side_effect = Exception(error_msg)
        
        # 调用测试方法并验证异常抛出
        with self.assertRaises(ValueError) as context:
            self.service.validate_and_convert_markdown(
                self.valid_markdown, 
                format='pptx', 
                theme='default'
            )
        
        # 验证异常消息
        self.assertIn(error_msg, str(context.exception))
        
        # 验证日志记录
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        self.assertIn("Markdown转换失败", args[0]) 