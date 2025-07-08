#!/usr/bin/env python
"""
知识点到PPT转换测试运行脚本

此脚本执行单元测试和集成测试，验证知识点到PPT转换功能
"""
import os
import sys
import logging
import django

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a7.settings')
django.setup()

# 导入Django测试工具
from django.test.runner import DiscoverRunner

def run_tests():
    """执行测试"""
    logger.info("开始执行知识点到PPT转换测试")
    
    # 指定要运行的测试
    test_labels = [
        'courses.tests.test_knowledge_to_ppt_conversion',
        'courses.tests.test_knowledge_to_ppt_integration'
    ]
    
    # 创建测试运行器
    test_runner = DiscoverRunner(
        verbosity=2,
        interactive=True,
        failfast=False
    )
    
    # 运行测试
    failures = test_runner.run_tests(test_labels)
    
    if failures:
        logger.error(f"测试失败: {failures} 个测试用例失败")
        return False
    else:
        logger.info("所有测试通过!")
        return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 