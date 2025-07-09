import os
import tempfile
import unittest
from unittest import mock

from django.test import TestCase, override_settings
from django.conf import settings

from marp_service import convert_markdown_to_format
from marp_service.cli import MarpCLIBuilder, MarpCLIExecutor


class HierarchyThemesTests(TestCase):
    """测试知识点层级主题功能"""
    
    def setUp(self):
        # 创建临时目录用于测试输出
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 测试样本 Markdown 内容
        self.test_markdown = """---
marp: true
theme: hierarchy-default
class: hierarchy
paginate: true
---

# 测试标题 {.level-1}

<!-- _class: level-1 -->

知识点层级演示

---

<!-- level: 2 -->

## 子知识点一 {.level-2}

<!-- _class: level-2 -->

<div class="content level-2-content">
这是一个二级知识点的内容示例。
</div>

---

<!-- level: 3 -->

### 深层知识点 {.level-3}

<!-- _class: level-3 -->

<div class="content level-3-content">
这是一个三级知识点的内容。
</div>
"""

    def tearDown(self):
        # 清理临时目录
        self.temp_dir.cleanup()

    @unittest.skipIf(
        not os.environ.get('RUN_MARP_TESTS'),
        "跳过需要实际marp-cli调用的测试，设置RUN_MARP_TESTS=1运行"
    )
    def test_hierarchy_default_theme(self):
        """测试默认层级主题"""
        # 构建主题目录路径
        theme_dir = os.path.join(settings.BASE_DIR, 'marp_service', 'themes')
        
        # 确保主题目录存在
        self.assertTrue(os.path.exists(theme_dir), "主题目录不存在")
        
        # 确保默认层级主题文件存在
        theme_file = os.path.join(theme_dir, 'hierarchy-default.css')
        self.assertTrue(os.path.exists(theme_file), "默认层级主题文件不存在")
        
        try:
            # 输出文件路径
            output_path = os.path.join(self.temp_dir.name, 'test_hierarchy.pdf')
            
            # 测试转换
            convert_markdown_to_format(
                content=self.test_markdown,
                output_format='pdf',
                output_path=output_path,
                theme='hierarchy-default',
                theme_dir=theme_dir
            )
            
            # 验证输出文件已生成
            self.assertTrue(os.path.exists(output_path), f"输出文件未生成: {output_path}")
            
            # 验证文件大小大于0
            self.assertGreater(os.path.getsize(output_path), 0, "生成的文件为空")
            
        except Exception as e:
            self.fail(f"测试默认层级主题时失败: {e}")
    
    @unittest.skipIf(
        not os.environ.get('RUN_MARP_TESTS'),
        "跳过需要实际marp-cli调用的测试，设置RUN_MARP_TESTS=1运行"
    )
    def test_style_options_injection(self):
        """测试注入自定义样式选项"""
        try:
            # 输出文件路径
            output_path = os.path.join(self.temp_dir.name, 'test_style_options.pdf')
            
            # 自定义样式选项
            style_options = {
                "--color-primary": "#ff0000",  # 红色
                "--color-secondary": "#00ff00",  # 绿色
                "--color-tertiary": "#0000ff",  # 蓝色
            }
            
            # 测试转换
            convert_markdown_to_format(
                content=self.test_markdown,
                output_format='pdf',
                output_path=output_path,
                theme='default',  # 使用默认主题
                style_options=style_options
            )
            
            # 验证输出文件已生成
            self.assertTrue(os.path.exists(output_path), f"输出文件未生成: {output_path}")
            
            # 验证文件大小大于0
            self.assertGreater(os.path.getsize(output_path), 0, "生成的文件为空")
            
        except Exception as e:
            self.fail(f"测试样式选项注入时失败: {e}")
            
    def test_marp_cli_builder_with_theme_dir(self):
        """测试MarpCLIBuilder支持主题目录和样式选项"""
        theme_dir = "/path/to/themes"  # 模拟路径
        
        # 通过模拟os.path.exists和os.path.isdir，使其返回True
        with mock.patch('os.path.exists', return_value=True):
            with mock.patch('os.path.isdir', return_value=True):
                builder = MarpCLIBuilder()
                builder.set_format('pdf')
                builder.add_theme('hierarchy-default')
                builder.add_theme_dir(theme_dir)
                builder.add_style_options({"--color-primary": "#ff0000"})
                
                args = builder.build()
                
                # 验证参数包含主题目录设置
                self.assertIn('--theme-set', args)
                self.assertIn(theme_dir, args)
                
                # 验证参数包含样式选项
                self.assertIn('--style-css', args)
                
                # 检查样式内容
                style_arg_index = args.index('--style-css')
                style_content = args[style_arg_index + 1]
                self.assertIn(':root', style_content)
                self.assertIn('--color-primary: #ff0000', style_content) 