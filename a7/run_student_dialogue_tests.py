#!/usr/bin/env python
"""
学生对话API测试运行脚本

此脚本运行学生对话API的所有测试，包括单元测试和集成测试。
"""
import os
import sys
import django
from django.core.management import call_command

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a7.settings')
django.setup()

def run_all_tests():
    """运行所有学生对话API测试"""
    print("="*80)
    print("运行学生对话API单元测试...")
    print("="*80)
    call_command('test', 'ai_services.tests.test_student_dialogue', verbosity=2)
    
    print("\n")
    print("="*80)
    print("运行学生对话API错误处理测试...")
    print("="*80)
    call_command('test', 'ai_services.tests.test_student_dialogue_integration.StudentDialogueErrorHandlingTest', verbosity=2)
    
    try:
        print("\n")
        print("="*80)
        print("运行学生对话API集成测试（需要n8n服务可用）...")
        print("注意：如果n8n服务不可用，这些测试将失败。")
        print("="*80)
        call_command('test', 'ai_services.tests.test_student_dialogue_integration.StudentDialogueIntegrationTest', verbosity=2)
    except Exception as e:
        print(f"集成测试失败：{str(e)}")
        print("这可能是因为n8n服务不可用。请确保n8n服务正在运行，并且配置了正确的webhook URL。")

def run_unit_tests_only():
    """只运行单元测试"""
    print("="*80)
    print("运行学生对话API单元测试...")
    print("="*80)
    call_command('test', 'ai_services.tests.test_student_dialogue', verbosity=2)
    
    print("\n")
    print("="*80)
    print("运行学生对话API错误处理测试...")
    print("="*80)
    call_command('test', 'ai_services.tests.test_student_dialogue_integration.StudentDialogueErrorHandlingTest', verbosity=2)

def run_integration_tests_only():
    """只运行集成测试"""
    try:
        print("="*80)
        print("运行学生对话API集成测试（需要n8n服务可用）...")
        print("注意：如果n8n服务不可用，这些测试将失败。")
        print("="*80)
        call_command('test', 'ai_services.tests.test_student_dialogue_integration.StudentDialogueIntegrationTest', verbosity=2)
    except Exception as e:
        print(f"集成测试失败：{str(e)}")
        print("这可能是因为n8n服务不可用。请确保n8n服务正在运行，并且配置了正确的webhook URL。")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--unit-only':
            run_unit_tests_only()
        elif sys.argv[1] == '--integration-only':
            run_integration_tests_only()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("可用参数: --unit-only, --integration-only")
            sys.exit(1)
    else:
        run_all_tests() 