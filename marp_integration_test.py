#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Marp服务API集成测试脚本
独立于Django测试框架，直接测试API端点功能
"""

import os
import sys
import json
import time
import requests
import argparse
from pathlib import Path

# 测试配置
DEFAULT_URL = "http://127.0.0.1:8000/api/marp/convert/"
TEST_FORMATS = ["pdf", "pptx", "html", "png"]
OUTPUT_DIR = "marp_test_output"


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


def run_integration_tests(api_url):
    """运行所有集成测试"""
    print("=" * 60)
    print(f"开始Marp API集成测试 - 端点: {api_url}")
    print("=" * 60)
    
    # 设置测试环境
    setup_test_environment()
    
    # 测试所有格式
    results = {}
    for fmt in TEST_FORMATS:
        results[fmt] = test_convert_markdown(api_url, fmt)
    
    # 测试带主题的转换
    theme_result = test_convert_markdown(api_url, "pdf", theme="default")
    
    # 测试无效请求
    test_invalid_requests(api_url)
    
    # 显示测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print("=" * 60)
    
    all_passed = True
    for fmt, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{fmt.upper()} 格式转换: {status}")
        if not passed:
            all_passed = False
    
    theme_status = "✅ 通过" if theme_result else "❌ 失败"
    print(f"带主题的转换: {theme_status}")
    
    print("\n总体结果:", "✅ 全部通过" if all_passed and theme_result else "❌ 部分或全部失败")
    
    return all_passed and theme_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Marp API集成测试")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"API端点URL (默认: {DEFAULT_URL})")
    args = parser.parse_args()
    
    success = run_integration_tests(args.url)
    sys.exit(0 if success else 1) 