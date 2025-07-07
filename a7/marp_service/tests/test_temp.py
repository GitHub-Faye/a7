import os
import tempfile
from unittest import mock

from django.test import TestCase

from ..exceptions import MarpFileError
from ..temp import MarpTempFileManager


class MarpTempFileManagerTests(TestCase):
    """测试MarpTempFileManager类"""
    
    def test_create_temp_markdown_file(self):
        """测试创建临时Markdown文件"""
        manager = MarpTempFileManager()
        test_content = "# Test Markdown\n\nThis is a test."
        
        try:
            with manager.create_temp_markdown_file(test_content) as temp_path:
                # 检查文件是否存在
                self.assertTrue(os.path.exists(temp_path))
                
                # 检查内容是否正确写入
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertEqual(content, test_content)
                
                # 记录临时文件路径以便后续检查
                self.temp_path = temp_path
            
            # 上下文管理器退出后，文件应该仍然存在（直到调用cleanup）
            self.assertTrue(os.path.exists(self.temp_path))
            
        finally:
            # 确保清理
            manager.cleanup()
            
            # 确认清理成功
            if hasattr(self, 'temp_path'):
                self.assertFalse(os.path.exists(self.temp_path))
    
    def test_get_temp_output_path(self):
        """测试获取临时输出路径"""
        manager = MarpTempFileManager()
        
        try:
            # 测试生成输出路径
            output_path = manager.get_temp_output_path('test_output', '.pdf')
            
            # 检查路径是否正确
            self.assertTrue(output_path.endswith('.pdf'))
            self.assertIn('test_output', output_path)
            
            # 目录应该已创建
            self.assertTrue(os.path.exists(os.path.dirname(output_path)))
            
        finally:
            # 确保清理
            manager.cleanup()
            
            # 确认清理成功
            if 'output_path' in locals():
                self.assertFalse(os.path.exists(os.path.dirname(output_path)))
    
    def test_cleanup(self):
        """测试清理功能"""
        manager = MarpTempFileManager()
        
        # 创建多个临时文件
        with manager.create_temp_markdown_file("Test 1") as path1:
            with manager.create_temp_markdown_file("Test 2") as path2:
                output_path = manager.get_temp_output_path('output', '.pdf')
                
                # 确认所有文件/目录都存在
                self.assertTrue(os.path.exists(path1))
                self.assertTrue(os.path.exists(path2))
                self.assertTrue(os.path.exists(os.path.dirname(output_path)))
                
                # 保存路径以供后续检查
                self.paths = [path1, path2, output_path]
                self.temp_dir = os.path.dirname(output_path)
        
        # 执行清理
        manager.cleanup()
        
        # 检查所有文件和目录是否都已删除
        for path in self.paths:
            self.assertFalse(os.path.exists(path))
        
        self.assertFalse(os.path.exists(self.temp_dir))
    
    @mock.patch('os.remove')
    def test_cleanup_error_handling(self, mock_remove):
        """测试清理过程中的错误处理"""
        manager = MarpTempFileManager()
        
        # 模拟删除文件时出错
        mock_remove.side_effect = OSError("模拟删除错误")
        
        # 创建临时文件
        with manager.create_temp_markdown_file("Test content") as temp_path:
            # 保存路径以供后续检查
            pass
        
        # 执行清理（不应该抛出异常）
        manager.cleanup()
        
        # 确认尝试删除文件
        mock_remove.assert_called() 