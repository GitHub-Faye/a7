#!/usr/bin/env python
"""
Marp集成测试脚本 - 知识点转PPT完整流程测试

用法:
    python marp_integration_test.py --use-ai  # 使用AI生成Markdown
    python marp_integration_test.py --format pdf  # 指定输出格式
    python marp_integration_test.py --output-dir ./output  # 指定输出目录
"""

import os
import sys
import json
import django
import argparse
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置Django环境
sys.path.append('a7')  # 将a7添加到Python路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a7.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from courses.models import Course, KnowledgePoint
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService
from marp_service.validation import MarkdownValidator
from ai_services.services.n8n_webhook.client import N8nWebhookClient

User = get_user_model()


class MarpIntegrationTest:
    """Marp集成测试类，测试知识点转PPT流程"""
    
    def __init__(self, use_ai=False, output_format='pptx', output_dir=None):
        """
        初始化测试环境
        
        Args:
            use_ai: 是否使用AI生成Markdown
            output_format: 输出格式 (pptx, pdf, html)
            output_dir: 输出目录
        """
        self.use_ai = use_ai
        self.output_format = output_format
        self.output_dir = output_dir or os.path.join(settings.BASE_DIR, 'marp_test_output')
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化服务
        self.service = KnowledgePointToPPTService()
        
        # 记录测试时间
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"初始化Marp集成测试: use_ai={use_ai}, format={output_format}")

    def setup_test_data(self):
        """创建测试数据"""
        logger.info("创建测试数据")
        
        try:
            # 创建测试用户
            self.teacher = User.objects.get_or_create(
                username='test_teacher',
                defaults={
                    'email': 'teacher@example.com',
                    'is_active': True
                }
            )[0]
            
            # 创建课程
            self.course = Course.objects.get_or_create(
                title='Python编程基础',
                defaults={
                    'subject': '计算机科学',
                    'grade_level': '大学',
                    'teacher': self.teacher
                }
            )[0]
            
            # 创建层次化的知识点结构
            self.kp_parent = KnowledgePoint.objects.get_or_create(
                title='Python基础语法',
                course=self.course,
                defaults={
                    'content': 'Python是一种易学且功能强大的编程语言。它的设计哲学强调代码的可读性和简洁的语法，这使得学习和理解Python变得容易。',
                    'importance': 5
                }
            )[0]
            
            # 创建子知识点1
            self.kp_child1 = KnowledgePoint.objects.get_or_create(
                title='变量和数据类型',
                course=self.course,
                parent=self.kp_parent,
                defaults={
                    'content': '''Python中的基本数据类型包括：
- 整数 (int): 如 1, 100, -10
- 浮点数 (float): 如 3.14, 0.001
- 字符串 (str): 如 "Hello", 'Python'
- 布尔值 (bool): True 或 False
- 列表 (list): 如 [1, 2, 3]
- 元组 (tuple): 如 (1, 2, 3)
- 字典 (dict): 如 {"name": "Python", "version": 3.9}
''',
                    'importance': 4
                }
            )[0]
            
            # 创建子知识点1的子知识点
            self.kp_grandchild = KnowledgePoint.objects.get_or_create(
                title='列表推导式',
                course=self.course,
                parent=self.kp_child1,
                defaults={
                    'content': '''列表推导式是Python中一种简洁的创建列表的方法。

基本语法:
```python
[表达式 for 变量 in 可迭代对象 if 条件]
```

示例:
```python
# 生成1到10的平方列表
squares = [x**2 for x in range(1, 11)]
# 结果: [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# 只获取偶数的平方
even_squares = [x**2 for x in range(1, 11) if x % 2 == 0]
# 结果: [4, 16, 36, 64, 100]
```
''',
                    'importance': 3
                }
            )[0]
            
            # 创建子知识点2
            self.kp_child2 = KnowledgePoint.objects.get_or_create(
                title='控制流',
                course=self.course,
                parent=self.kp_parent,
                defaults={
                    'content': '''Python提供了多种控制流语句，包括:

1. 条件语句
```python
if condition1:
    # 代码块1
elif condition2:
    # 代码块2
else:
    # 代码块3
```

2. 循环语句
- for循环:
```python
for i in range(5):
    print(i)  # 输出: 0, 1, 2, 3, 4
```

- while循环:
```python
count = 0
while count < 5:
    print(count)  # 输出: 0, 1, 2, 3, 4
    count += 1
```
''',
                    'importance': 4
                }
            )[0]
            
            logger.info("测试数据创建完成")
            
            # 返回知识点ID列表，便于后续使用
            return [self.kp_parent.id]
            
        except Exception as e:
            logger.error(f"创建测试数据失败: {e}")
            raise
    
    def run_test(self):
        """运行集成测试"""
        logger.info(f"开始运行集成测试 (AI生成: {self.use_ai})")
        
        try:
            # 创建测试数据并获取知识点ID
            knowledge_point_ids = self.setup_test_data()
            
            # 准备请求数据
            data = {
                "knowledge_point_ids": knowledge_point_ids,
                "include_children": True,
                "max_depth": 3,
                "format": self.output_format,
                "theme": "default",
                "use_ai": self.use_ai,
                "title": f"Python基础知识测试 {'(AI生成)' if self.use_ai else '(本地生成)'}"
            }
            
            # 记录请求详情
            logger.info(f"处理请求参数: {data}")
            
            # 1. 获取知识点层次结构
            knowledge_data = self.service.fetch_knowledge_points_hierarchy(
                data["knowledge_point_ids"],
                data.get("include_children", True),
                data.get("max_depth", 3)
            )
            
            # 检查是否获取成功
            if "error" in knowledge_data:
                logger.error(f"获取知识点数据失败: {knowledge_data['error']}")
                return False
                
            logger.info(f"获取到 {len(knowledge_data['knowledge_points'])} 个顶级知识点")
            
            # 2. 保存知识点数据到JSON文件
            knowledge_file = os.path.join(self.output_dir, f"knowledge_data_{self.timestamp}.json")
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
            logger.info(f"知识点数据已保存到: {knowledge_file}")
            
            # 3. 生成Markdown
            if self.use_ai:
                logger.info("使用AI服务生成Markdown...")
                markdown_content = self.service.generate_markdown_using_ai(
                    knowledge_data,
                    data.get("title"),
                    True,
                    data.get("theme", "default")
                )
            else:
                logger.info("使用本地逻辑生成Markdown...")
                markdown_content = self.service.generate_markdown_from_knowledge_points(
                    knowledge_data,
                    data.get("title"),
                    True
                )
            
            # 4. 保存生成的Markdown
            md_file = os.path.join(self.output_dir, f"generated_markdown_{self.timestamp}.md")
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"生成的Markdown已保存到: {md_file}")
            
            # 5. 验证Markdown
            logger.info("验证Markdown内容...")
            validator = MarkdownValidator(markdown_content)
            is_valid = validator.validate()
            
            validation_result = {
                "valid": is_valid,
                "errors": validator.errors,
                "warnings": validator.warnings
            }
            
            # 保存验证结果
            validation_file = os.path.join(self.output_dir, f"validation_result_{self.timestamp}.json")
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation_result, f, ensure_ascii=False, indent=2)
            logger.info(f"验证结果已保存到: {validation_file}")
            
            if not is_valid:
                logger.warning("Markdown验证失败，尝试修复...")
                logger.warning(f"错误: {validator.errors}")
                logger.warning(f"警告: {validator.warnings}")
                
                # 6. 修复Markdown
                fixed_markdown = validator.fix()
                
                # 保存修复后的Markdown
                fixed_md_file = os.path.join(self.output_dir, f"fixed_markdown_{self.timestamp}.md")
                with open(fixed_md_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_markdown)
                logger.info(f"修复后的Markdown已保存到: {fixed_md_file}")
                
                # 再次验证
                fixed_validator = MarkdownValidator(fixed_markdown)
                is_fixed_valid = fixed_validator.validate()
                
                if is_fixed_valid:
                    logger.info("Markdown修复成功!")
                    markdown_content = fixed_markdown
                else:
                    logger.error("Markdown修复后仍然无效!")
                    logger.error(f"错误: {fixed_validator.errors}")
                    logger.error(f"警告: {fixed_validator.warnings}")
            
            # 7. 转换为演示文稿
            logger.info(f"转换Markdown为{self.output_format}格式...")
            
            # 调整输出路径为我们指定的目录
            output_filename = f"presentation_{self.timestamp}.{self.output_format}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            try:
                from marp_service import convert_markdown_to_format
                convert_markdown_to_format(
                    content=markdown_content,
                    output_format=self.output_format,
                    output_path=output_path,
                    theme=data.get("theme", "default")
                )
                
                logger.info(f"演示文稿已成功生成: {output_path}")
                return True
                
            except Exception as e:
                logger.error(f"转换Markdown失败: {e}")
                return False
                
        except Exception as e:
            logger.error(f"集成测试失败: {e}", exc_info=True)
            return False


def main():
    """主函数，处理命令行参数并运行测试"""
    parser = argparse.ArgumentParser(description='运行Marp集成测试')
    parser.add_argument('--use-ai', action='store_true', help='使用AI生成Markdown')
    parser.add_argument('--format', choices=['pptx', 'pdf', 'html'], default='pptx', help='输出格式')
    parser.add_argument('--output-dir', help='输出目录')
    
    args = parser.parse_args()
    
    # 运行测试
    test = MarpIntegrationTest(
        use_ai=args.use_ai,
        output_format=args.format,
        output_dir=args.output_dir
    )
    
    success = test.run_test()
    
    if success:
        print("\n✅ 测试成功完成!")
        print(f"输出文件保存在: {test.output_dir}")
    else:
        print("\n❌ 测试失败!")
        print("请查看日志了解详情")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 