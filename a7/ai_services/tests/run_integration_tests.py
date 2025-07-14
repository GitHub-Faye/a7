#!/usr/bin/env python
"""
AI服务集成测试运行脚本

此脚本用于运行所有AI服务的集成测试，验证它们与n8n服务的集成情况。
使用方法：
    python run_integration_tests.py [--service SERVICE_NAME] [--all]

参数：
    --service SERVICE_NAME：指定要测试的服务名称，可选值为：
        dialogue: 学生对话服务
        questions: 问题生成服务
        exercises: 练习题生成服务
        answer: 答案校正服务
        course: 课程内容生成服务
        markdown: 知识点转Markdown服务
        ppt: 知识点转PPT服务
    --all：运行所有服务的集成测试
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a7.settings")

import django
django.setup()

# 服务名称映射到测试文件
SERVICE_TEST_FILES = {
    'dialogue': 'test_dialogue_with_student_integration.py',
    'questions': 'test_generate_questions_integration.py',
    'exercises': 'test_generate_exercises_integration.py',
    'answer': 'test_correct_student_answer_integration.py',
    'course': 'test_generate_course_content_integration.py',
    'markdown': 'test_generate_markdown_from_knowledge_integration.py',
    'ppt': 'test_knowledge_point_to_ppt_integration.py'
}

# 服务名称映射到友好名称
SERVICE_NAMES = {
    'dialogue': '学生对话服务(dialogue_with_student)',
    'questions': '问题生成服务(generate_questions)',
    'exercises': '练习题生成服务(generate_exercises)',
    'answer': '答案校正服务(correct_student_answer)',
    'course': '课程内容生成服务(generate_course_content)',
    'markdown': '知识点转Markdown服务(generate_markdown_from_knowledge)',
    'ppt': '知识点转PPT服务(KnowledgePointToPPT)'
}


def run_test(service_name):
    """运行指定服务的集成测试"""
    if service_name not in SERVICE_TEST_FILES:
        print(f"❌ 未知服务名称: {service_name}")
        return False
    
    test_file = SERVICE_TEST_FILES[service_name]
    friendly_name = SERVICE_NAMES[service_name]
    
    print(f"\n{'='*80}")
    print(f"🧪 运行 {friendly_name} 集成测试")
    print(f"{'='*80}")
    
    test_path = os.path.join(BASE_DIR, 'ai_services', 'tests', test_file)
    
    try:
        # 使用pytest运行测试，直接将输出传递到控制台
        cmd = [sys.executable, '-m', 'pytest', test_path, '-v']
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        
        # 检查返回码
        if result.returncode == 0:
            print(f"✅ {friendly_name} 集成测试通过")
            return True
        else:
            print(f"❌ {friendly_name} 集成测试失败")
            return False
    
    except Exception as e:
        print(f"❌ 运行测试时出错: {str(e)}")
        return False


def run_all_tests():
    """运行所有服务的集成测试"""
    print(f"\n{'='*80}")
    print(f"🧪 运行所有AI服务的集成测试")
    print(f"{'='*80}")
    
    # 存储结果的字典
    results = {}
    start_time = time.time()
    
    for service_name in SERVICE_TEST_FILES:
        results[service_name] = run_test(service_name)
    
    # 输出汇总结果
    print(f"\n{'='*80}")
    print(f"📊 测试结果汇总")
    print(f"{'='*80}")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for service_name, passed in results.items():
        friendly_name = SERVICE_NAMES[service_name]
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{friendly_name}: {status}")
    
    total_time = time.time() - start_time
    print(f"\n总结: {success_count}/{total_count} 个服务测试通过")
    print(f"总耗时: {total_time:.2f}秒")
    
    # 如果全部测试通过，则返回True
    return success_count == total_count


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行AI服务的集成测试')
    parser.add_argument('--service', type=str, help='要测试的服务名称')
    parser.add_argument('--all', action='store_true', help='运行所有服务的集成测试')
    
    args = parser.parse_args()
    
    if args.service:
        run_test(args.service)
    elif args.all:
        run_all_tests()
    else:
        # 如果没有指定参数，则默认运行所有测试
        run_all_tests()


if __name__ == '__main__':
    main() 