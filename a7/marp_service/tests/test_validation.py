import unittest
from django.test import TestCase
from marp_service.validation import MarkdownValidator

class MarkdownValidatorTestCase(TestCase):
    """测试MarkdownValidator类的功能"""
    
    def test_validate_good_markdown(self):
        """测试有效的Markdown内容验证"""
        # 创建标准格式的Markdown内容
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页

内容

---

## 第一节

- 列表项1
- 列表项2

---

### 第一节的子节

内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证通过，没有错误
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
        self.assertEqual(len(validator.warnings), 0)
    
    def test_validate_missing_frontmatter(self):
        """测试缺少前置元数据的情况"""
        markdown = """# 标题页

内容

---

## 第一节

内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证失败，有错误
        self.assertFalse(validator.validate())
        self.assertGreater(len(validator.errors), 0)
        
        # 检查具体错误
        self.assertIn("缺少前置元数据区域", validator.errors[0])
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容
        fixed_validator = MarkdownValidator(fixed)
        self.assertTrue(fixed_validator.validate())
    
    def test_validate_missing_marp_directive(self):
        """测试缺少marp指令的情况"""
        markdown = """---
theme: default
paginate: true
---

# 标题页

内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证失败，有错误
        self.assertFalse(validator.validate())
        self.assertIn("缺少必要的marp配置", validator.errors[0])
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容
        fixed_validator = MarkdownValidator(fixed)
        self.assertTrue(fixed_validator.validate())
        self.assertTrue("marp: true" in fixed)
    
    def test_validate_missing_theme(self):
        """测试缺少主题的情况"""
        markdown = """---
marp: true
paginate: true
---

# 标题页

内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证通过，但有警告
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
        self.assertGreater(len(validator.warnings), 0)
        self.assertIn("缺少主题配置", validator.warnings[0])
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容
        fixed_validator = MarkdownValidator(fixed)
        self.assertTrue(fixed_validator.validate())
        self.assertEqual(len(fixed_validator.warnings), 0)
        self.assertTrue("theme: default" in fixed)
    
    def test_validate_slide_structure(self):
        """测试幻灯片结构验证"""
        # 只有一张幻灯片，结构不完整
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页
"""
        validator = MarkdownValidator(markdown)
        
        # 虽然只有一张幻灯片，但结构正确，应该通过
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
    
    def test_validate_slide_separators(self):
        """测试幻灯片分隔符验证"""
        # 分隔符格式不正确（多出一个分隔符）
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页

内容

---

## 第一节

内容

---
"""
        validator = MarkdownValidator(markdown)
        
        # 应该有警告
        validator.validate()
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容不以---结尾
        self.assertFalse(fixed.strip().endswith("---"))
    
    def test_validate_hierarchy(self):
        """测试层级结构验证"""
        # 标题层级跳跃
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页

内容

---

### 标题跳过二级直接到三级

内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证通过，但有警告
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
        
        # 应该有层级跳跃的警告
        hierarchy_warnings = [w for w in validator.warnings if "标题层级跳跃" in w]
        self.assertGreater(len(hierarchy_warnings), 0)
    
    def test_validate_empty_content(self):
        """测试空内容幻灯片验证"""
        # 有标题无内容的幻灯片
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页

内容

---

## 只有标题没有内容

---

## 另一个标题

有内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证通过，但有警告
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
        
        # 应该有内容为空的警告
        content_warnings = [w for w in validator.warnings if "只有标题没有内容" in w]
        self.assertGreater(len(content_warnings), 0)
    
    def test_validate_code_blocks(self):
        """测试代码块验证"""
        # 未闭合的代码块
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页

```python
def hello():
    print("Hello, world!")
# 没有闭合的代码块

---

## 第二页

内容
"""
        validator = MarkdownValidator(markdown)
        
        # 验证失败，有错误
        self.assertFalse(validator.validate())
        self.assertIn("未闭合的代码块", validator.errors[0])
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容
        fixed_validator = MarkdownValidator(fixed)
        self.assertTrue(fixed_validator.validate())
        self.assertTrue("```" in fixed and fixed.count("```") % 2 == 0)
    
    def test_validate_list_markers(self):
        """测试列表标记符号验证"""
        # 混合使用不同的列表标记
        markdown = """---
marp: true
theme: default
paginate: true
---

# 标题页

- 列表项1
* 列表项2
+ 列表项3
"""
        validator = MarkdownValidator(markdown)
        
        # 验证通过，但有警告
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
        
        # 应该有列表标记混用的警告
        list_warnings = [w for w in validator.warnings if "列表使用了不同的标记符号" in w]
        self.assertGreater(len(list_warnings), 0)
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容
        self.assertTrue("- 列表项1" in fixed)
        self.assertTrue("- 列表项2" in fixed)
        self.assertTrue("- 列表项3" in fixed)
        
    def test_fix_all_issues(self):
        """测试修复多个问题"""
        # 包含多种问题的Markdown
        markdown = """# 没有前置元数据的标题页

- 列表项1
* 混合列表标记
+ 另一个混合标记

---

### 跳级标题

```python
未闭合的代码块
"""
        validator = MarkdownValidator(markdown)
        
        # 验证失败，有多个错误
        self.assertFalse(validator.validate())
        self.assertGreater(len(validator.errors), 0)
        
        # 修复
        fixed = validator.fix()
        
        # 验证修复后的内容
        fixed_validator = MarkdownValidator(fixed)
        self.assertTrue(fixed_validator.validate())
        
        # 检查所有问题是否都已修复
        self.assertIn("---", fixed)  # 添加了前置元数据
        self.assertIn("marp: true", fixed)  # 添加了marp指令
        self.assertIn("theme: default", fixed)  # 添加了主题
        self.assertTrue(fixed.count("```") % 2 == 0)  # 修复了代码块
        
        # 检查列表标记是否已统一
        self.assertIn("- 列表项1", fixed)
        self.assertIn("- 混合列表标记", fixed)
        self.assertIn("- 另一个混合标记", fixed) 