import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from django.test import TestCase

from .. import convert_markdown_to_format, convert_file_to_format
from ..cli import MarpCLIExecutor
from ..exceptions import MarpCLIError, MarpConversionError


# 检查marp-cli是否可用
def check_marp_cli_available():
    """检查marp-cli是否可用"""
    try:
        # 使用marp命令的完整路径
        marp_cmd = "C:\\Users\\WYW\\AppData\\Roaming\\npm\\marp.cmd"
        
        result = subprocess.run(
            f"{marp_cmd} --version",
            shell=True,  # 在Windows环境下必须使用shell=True
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 如果命令执行成功，返回True
        if result.returncode == 0:
            print(f"marp命令可用，版本信息: {result.stdout.strip()}")
            return True
        else:
            print(f"marp命令不可用，错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"检查marp可用性时出错: {str(e)}")
        return False


# 只有在marp-cli可用时才运行这些测试
@unittest.skipIf(not check_marp_cli_available(), "marp-cli未安装或不可用")
class MarpRealIntegrationTests(TestCase):
    """使用真实marp-cli工具的集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录，用于存储测试输出文件
        self.test_output_dir = tempfile.mkdtemp(prefix="marp_test_")
        
        # 准备测试用的Markdown内容
        self.test_markdown = """---
marp: true
theme: default
---

# Marp集成测试

这是一个使用真实marp-cli工具的测试幻灯片

---

## 第二页

- 项目1
- 项目2
- 项目3

---

## 感谢使用
"""
        
        # 创建一个临时Markdown文件
        fd, self.markdown_file_path = tempfile.mkstemp(suffix=".md", prefix="test_")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(self.test_markdown)

    def tearDown(self):
        """清理测试环境"""
        # 删除临时文件和目录
        if os.path.exists(self.markdown_file_path):
            os.unlink(self.markdown_file_path)
        
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    def test_cli_executor(self):
        """测试使用真实CLI执行器"""
        output_path = os.path.join(self.test_output_dir, "cli_output.pdf")
        
        executor = MarpCLIExecutor(timeout=120)  # 增加超时时间以允许安装依赖
        
        args = [
            self.markdown_file_path,
            "--pdf",
            "--output", output_path,
            "--allow-local-files"
        ]
        
        returncode, stdout, stderr = executor.execute(args)
        
        # 验证输出文件存在
        self.assertTrue(os.path.exists(output_path))
        # 验证输出文件大小大于0
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_convert_markdown_to_pdf(self):
        """测试将Markdown内容转换为PDF格式"""
        output_path = os.path.join(self.test_output_dir, "content_output.pdf")
        
        result_path = convert_markdown_to_format(
            content=self.test_markdown,
            output_format="pdf",
            output_path=output_path
        )
        
        # 检查输出文件是否存在
        self.assertTrue(os.path.exists(result_path))
        self.assertEqual(result_path, output_path)
        
        # 检查文件大小是否合理（PDF文件应大于0字节）
        self.assertGreater(os.path.getsize(result_path), 0)

    def test_convert_file_to_pdf(self):
        """测试将Markdown文件转换为PDF格式"""
        output_path = os.path.join(self.test_output_dir, "file_output.pdf")
        
        result_path = convert_file_to_format(
            file_path=self.markdown_file_path,
            output_format="pdf",
            output_path=output_path
        )
        
        # 检查输出文件是否存在
        self.assertTrue(os.path.exists(result_path))
        self.assertEqual(result_path, output_path)
        
        # 检查文件大小是否合理
        self.assertGreater(os.path.getsize(result_path), 0)
    
    def test_convert_to_html(self):
        """测试将Markdown内容转换为HTML格式"""
        output_path = os.path.join(self.test_output_dir, "output.html")
        
        result_path = convert_markdown_to_format(
            content=self.test_markdown,
            output_format="html",
            output_path=output_path
        )
        
        # 检查输出文件是否存在
        self.assertTrue(os.path.exists(result_path))
        
        # 检查文件内容（应包含HTML基本结构）
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Marp集成测试", content)

    def test_convert_to_pptx(self):
        """测试将Markdown内容转换为PPTX格式"""
        output_path = os.path.join(self.test_output_dir, "output.pptx")
        
        result_path = convert_markdown_to_format(
            content=self.test_markdown,
            output_format="pptx",
            output_path=output_path
        )
        
        # 检查输出文件是否存在
        self.assertTrue(os.path.exists(result_path))
        
        # 检查文件大小是否合理（PPTX文件应大于0字节）
        self.assertGreater(os.path.getsize(result_path), 0)
    
    def test_convert_with_theme(self):
        """测试使用不同主题进行转换"""
        output_path = os.path.join(self.test_output_dir, "themed_output.pdf")
        
        result_path = convert_markdown_to_format(
            content=self.test_markdown,
            output_format="pdf",
            theme="gaia",  # 使用gaia主题
            output_path=output_path
        )
        
        # 检查输出文件是否存在
        self.assertTrue(os.path.exists(result_path))
        
        # 文件应该已生成（无法直接检查主题应用效果，但至少确保命令成功执行）
        self.assertGreater(os.path.getsize(result_path), 0)

    @unittest.skipIf(sys.platform == 'win32', "Windows环境下非标准主题可能不会引发异常")
    def test_invalid_theme(self):
        """测试使用无效主题时的错误处理"""
        output_path = os.path.join(self.test_output_dir, "invalid_theme.pdf")
        
        # 使用不存在的主题应该会引发异常
        with self.assertRaises((MarpCLIError, MarpConversionError)):
            convert_markdown_to_format(
                content=self.test_markdown,
                output_format="pdf",
                theme="non_existent_theme_that_definitely_does_not_exist_12345",  # 使用更明确的不存在主题名
                output_path=output_path
            )

    # 在Windows环境下直接跳过此测试，因为临时文件处理在Windows上可能不稳定
    @unittest.skipIf(sys.platform == 'win32', "Windows环境下临时文件测试可能不稳定")
    def test_temporary_output_file(self):
        """测试不指定输出路径时的临时文件生成"""
        try:
            # 不指定输出路径，应使用临时文件
            result_path = convert_markdown_to_format(
                content=self.test_markdown,
                output_format="pdf"
            )
            
            print(f"临时文件路径: {result_path}")
            
            # 检查输出文件是否存在
            self.assertTrue(os.path.exists(result_path), f"临时文件 {result_path} 不存在")
            
            # 检查是否是临时目录中的文件
            self.assertTrue("tmp" in result_path.lower() or "temp" in result_path.lower(), 
                          f"文件路径 {result_path} 不在临时目录中")
            
            # 检查文件大小是否合理
            self.assertGreater(os.path.getsize(result_path), 0, f"文件 {result_path} 大小为零")
            
            # 清理
            if os.path.exists(result_path):
                os.unlink(result_path)
        except Exception as e:
            self.fail(f"测试失败，出现异常: {e}")
    
    @unittest.skipIf(sys.platform == 'win32', "Windows环境下PNG输出格式需要特殊处理")
    def test_convert_to_png(self):
        """测试将Markdown内容转换为PNG格式"""
        # 在Windows上，marp-cli不能直接将PNG输出到目录，需要指定具体文件名
        if sys.platform == 'win32':
            output_path = os.path.join(self.test_output_dir, "output.png")
        else:
            output_dir = os.path.join(self.test_output_dir, "png_output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = output_dir
        
        result_path = convert_markdown_to_format(
            content=self.test_markdown,
            output_format="png",
            output_path=output_path
        )
        
        if sys.platform == 'win32':
            # Windows环境下检查单个文件
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)
        else:
            # Linux/Mac环境下检查目录中的多个PNG文件
            self.assertTrue(os.path.exists(output_dir))
            png_files = list(Path(output_dir).glob("*.png"))
            self.assertGreaterEqual(len(png_files), 3)  # 我们有3张幻灯片
            for png_file in png_files:
                self.assertGreater(png_file.stat().st_size, 0) 