#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Marp服务API集成测试脚本
独立于Django测试框架，直接测试API端点功能
"""

import os
import sys
import django
import json
import time
import requests
import argparse
from pathlib import Path

# 将项目根目录添加到Python路径
# D:\file\A7
current_dir = Path(__file__).resolve().parent
# D:\file\A7
project_root = current_dir

# 根据用户反馈，Django项目的根目录在'a7'子目录中。
# 我们需要将这个子目录添加到sys.path中，以便Django可以找到'a7.settings'模块。
django_root = project_root / 'a7'
sys.path.insert(0, str(django_root))

# 测试配置
DEFAULT_URL = "http://127.0.0.1:8000/api/marp/convert/"
TEST_FORMATS = ["pdf", "pptx", "html", "png"]
OUTPUT_DIR = "marp_test_output"


def setup_django():
    """手动配置Django环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a7.settings')
    try:
        django.setup()
    except ImportError:
        raise ImportError(
            "无法导入Django设置。请确保：\n"
            "1. 你在项目的根目录下运行此脚本。\n"
            "2. DJANGO_SETTINGS_MODULE环境变量已正确设置。\n"
            "3. a7.settings模块路径正确。\n"
        )


def setup_test_environment():
    """创建输出目录"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"测试输出将保存到: {os.path.abspath(OUTPUT_DIR)}")


def get_test_markdown():
    """返回测试用的Markdown内容"""
    return """
# Marp API 测试演示

---

## 幻灯片 2

- 项目符号 1
- 项目符号 2
- 项目符号 3

---

## 代码示例

```python
def hello_world():
    print("Hello from Marp API!")
```

---

## 表格示例

| 功能 | 状态 |
|------|------|
| PDF转换 | ✅ |
| PPTX转换 | ✅ |
| HTML转换 | ✅ |
| PNG转换 | ✅ |

---

## 谢谢!
    """


def test_convert_markdown(api_url, output_format, theme=None):
    """测试Markdown转换API"""
    print(f"\n测试转换为 {output_format.upper()} 格式" + (f" (主题: {theme})" if theme else ""))
    
    # 准备请求数据
    payload = {
        "content": get_test_markdown(),
        "format": output_format
    }
    
    if theme:
        payload["theme"] = theme
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 发送API请求
        response = requests.post(api_url, json=payload)
        elapsed_time = time.time() - start_time
        
        # 检查响应状态
        if response.status_code == 200:
            # 保存输出文件
            output_file = os.path.join(OUTPUT_DIR, f"output.{output_format}")
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_file)
            print(f"✅ 成功! 转换耗时: {elapsed_time:.2f}秒, 文件大小: {file_size/1024:.1f} KB")
            print(f"   保存到: {output_file}")
            return True
        else:
            # 尝试解析错误响应
            try:
                error_data = response.json()
                print(f"❌ 失败 (HTTP {response.status_code}): {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"❌ 失败 (HTTP {response.status_code}): {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 请求错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未预期的错误: {e}")
        return False


def test_invalid_requests(api_url):
    """测试各种无效请求的处理"""
    print("\n测试无效请求处理:")
    
    test_cases = [
        {
            "name": "缺少content字段",
            "payload": {"format": "pdf"}
        },
        {
            "name": "缺少format字段",
            "payload": {"content": "# Test"}
        },
        {
            "name": "无效的格式",
            "payload": {"content": "# Test", "format": "invalid"}
        },
        {
            "name": "无效的主题",
            "payload": {"content": "# Test", "format": "pdf", "theme": "nonexistent"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n- 测试: {test_case['name']}")
        try:
            response = requests.post(api_url, json=test_case["payload"])
            try:
                result = response.json()
                print(f"  响应 (HTTP {response.status_code}): {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                print(f"  响应 (HTTP {response.status_code}): {response.text}")
        except Exception as e:
            print(f"  错误: {e}")


def run_test(test_name, markdown_content, output_dir, theme, output_formats, style_options=None):
    """
    运行单个测试用例，生成多种格式的演示文稿。

    Args:
        test_name (str): 测试用例的名称。
        markdown_content (str): 用于转换的Markdown内容。
        output_dir (str): 输出目录。
        theme (str): 使用的主题名称。
        output_formats (list): 输出格式列表 (e.g., ['pptx', 'pdf', 'html'])。
        style_options (dict, optional): 样式选项。
    """
    print(f"--- Running Test: {test_name} ---")
    
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 获取自定义主题目录
    theme_dir = project_root / 'a7' / 'marp_service' / 'themes'
    if not theme_dir.exists():
        print(f"  [ERROR] 主题目录未找到: {theme_dir}")
        return

    from marp_service import convert_markdown_to_format

    for fmt in output_formats:
        output_filename = f"{test_name.replace(' ', '_').lower()}.{fmt}"
        output_path = Path(output_dir) / output_filename
        
        try:
            print(f"  -> Generating {fmt.upper()}...")
            convert_markdown_to_format(
                content=markdown_content,
                output_format=fmt,
                output_path=str(output_path),
                theme=theme,
                theme_dir=str(theme_dir),
                style_options=style_options
            )
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"  [SUCCESS] {fmt.upper()} 文件已生成: {output_path}")
            else:
                print(f"  [FAILURE] {fmt.upper()} 文件生成失败或为空。")
        except Exception as e:
            print(f"  [ERROR] 生成 {fmt.upper()} 时出错: {e}")
    print("-" * (len(test_name) + 20))


def main():
    """
    主函数，定义并运行所有集成测试。
    """
    # 初始化Django
    setup_django()

    # 通用测试Markdown内容
    test_markdown = """---
marp: true
paginate: true
header: 'A7-System'
footer: 'Integration Test'
---

# 1. 一级知识点

<!-- _class: level-1 -->

这是一级知识点的主要内容。

- 列表项 A
- 列表项 B

---

<!-- _class: level-1 -->

## 1.1 二级知识点 (A)

<!-- _class: level-2 -->

这是二级知识点 A 的详细说明。

```python
def hello_world():
    print("Hello from a level 2 slide!")
```

---

<!-- _class: level-1 -->

## 1.2 二级知识点 (B)

<!-- _class: level-2 -->

这是二级知识点 B 的详细说明。

> 这是一个引用块，用于强调重要信息。

---

<!-- _class: level-2 -->

### 1.2.1 三级知识点

<!-- _class: level-3 -->

这是三级知识点的具体内容。

| 表头1 | 表头2 |
|---|---|
| 单元格1 | 单元格2 |
| 单元格3 | 单元格4 |

"""

    # --- 定义测试用例 ---
    output_dir_base = project_root / "marp_test_output"
    formats_to_generate = ['pptx', 'pdf', 'html']

    # 测试1: 默认层级主题 (hierarchy-default)
    run_test(
        "Default Hierarchy Theme",
        test_markdown,
        output_dir=output_dir_base / "default_theme",
        theme="hierarchy-default",
        output_formats=formats_to_generate
    )

    # 测试2: 教学型主题 (hierarchy-teaching)
    run_test(
        "Teaching Hierarchy Theme",
        test_markdown.replace("marp: true", "marp: true\nclass: teaching"), # 添加教学型class
        output_dir=output_dir_base / "teaching_theme",
        theme="hierarchy-teaching",
        output_formats=formats_to_generate
    )

    # 测试3: 简洁型主题 (hierarchy-minimalist)
    run_test(
        "Minimalist Hierarchy Theme",
        test_markdown,
        output_dir=output_dir_base / "minimalist_theme",
        theme="hierarchy-minimalist",
        output_formats=formats_to_generate
    )

    # 测试4: 默认主题 + 红色配色方案
    run_test(
        "Default Theme with Red Scheme",
        test_markdown,
        output_dir=output_dir_base / "style_options",
        theme="hierarchy-default",
        output_formats=formats_to_generate,
        style_options={
            "--color-primary": "#e63946",
            "--color-secondary": "#f1726f",
            "--color-tertiary": "#f8998d"
        }
    )
    
    print("\n所有集成测试已完成。")
    print(f"请检查输出目录: {output_dir_base.resolve()}")


if __name__ == "__main__":
    main() 