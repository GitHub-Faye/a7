"""
测试问题格式验证和格式化功能
"""

from django.test import TestCase
from ai_services.services.question_format import QuestionFormatValidator, QuestionFormatter
import json


class QuestionFormatValidatorTests(TestCase):
    """测试问题格式验证功能"""
    
    def test_validate_single_choice_question(self):
        """测试单选题格式验证"""
        # 准备有效的单选题数据
        valid_question = {
            "title": "测试单选题",
            "content": "这是一道测试单选题",
            "type": "single_choice",
            "difficulty": 3,
            "answer_template": ["选项A", "选项B", "选项C", "选项D"],
            "knowledge_point_id": 1
        }
        
        # 验证有效数据
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([valid_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        
        # 测试无效数据（缺少必填字段）
        invalid_question = valid_question.copy()
        del invalid_question["answer_template"]
        result, errors = validator.validate_questions([invalid_question])
        self.assertEqual(len(result), 0)
        self.assertEqual(len(errors), 1)
        
    def test_validate_multiple_choice_question(self):
        """测试多选题格式验证"""
        # 准备有效的多选题数据
        valid_question = {
            "title": "测试多选题",
            "content": "这是一道测试多选题",
            "type": "multiple_choice",
            "difficulty": 3,
            "answer_template": ["选项A", "选项B", "选项C", "选项D", "选项E"],
            "knowledge_point_id": 1
        }
        
        # 验证有效数据
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([valid_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        
        # 测试选项不足的情况
        invalid_question = valid_question.copy()
        invalid_question["answer_template"] = ["选项A", "选项B"]
        result, errors = validator.validate_questions([invalid_question])
        self.assertEqual(len(result), 0)
        self.assertEqual(len(errors), 1)
        
    def test_validate_fill_blank_question(self):
        """测试填空题格式验证"""
        # 准备有效的填空题数据
        valid_question = {
            "title": "测试填空题",
            "content": "这是一道___测试填空题",
            "type": "fill_blank",
            "difficulty": 3,
            "answer_template": ["答案A", "答案B"],
            "knowledge_point_id": 1
        }
        
        # 验证有效数据
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([valid_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        
        # 测试无填空标记但仍然有效的情况（应该只有警告）
        valid_with_warning = valid_question.copy()
        valid_with_warning["content"] = "这是一道测试填空题，没有明确的填空标记"
        result, errors = validator.validate_questions([valid_with_warning])
        self.assertEqual(len(result), 1)  # 不阻止验证通过
        self.assertEqual(len(errors), 0)
        
    def test_validate_short_answer_question(self):
        """测试简答题格式验证"""
        # 准备有效的简答题数据
        valid_question = {
            "title": "测试简答题",
            "content": "这是一道测试简答题",
            "type": "short_answer",
            "difficulty": 3,
            "answer_template": "这是参考答案",
            "knowledge_point_id": 1
        }
        
        # 验证有效数据
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([valid_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        
    def test_validate_coding_question(self):
        """测试编程题格式验证"""
        # 准备有效的编程题数据
        valid_question = {
            "title": "测试编程题",
            "content": "这是一道测试编程题",
            "type": "coding",
            "difficulty": 3,
            "answer_template": "def solution():\n    return True",
            "knowledge_point_id": 1
        }
        
        # 验证有效数据
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([valid_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        
        # 测试列表形式的答案模板转换
        list_template_question = valid_question.copy()
        list_template_question["answer_template"] = [
            "def solution():",
            "    return True"
        ]
        result, errors = validator.validate_questions([list_template_question])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(errors), 0)
        self.assertIsInstance(result[0]["answer_template"], str)  # 确认已转换为字符串
        
    def test_invalid_difficulty(self):
        """测试无效的难度级别"""
        # 准备难度级别无效的问题
        invalid_question = {
            "title": "测试题",
            "content": "测试内容",
            "type": "single_choice",
            "difficulty": 10,  # 超出有效范围
            "answer_template": ["A", "B", "C"],
            "knowledge_point_id": 1
        }
        
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([invalid_question])
        self.assertEqual(len(result), 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("难度级别", errors[0])
        
    def test_unsupported_type(self):
        """测试不支持的题型"""
        # 准备类型无效的问题
        invalid_question = {
            "title": "测试题",
            "content": "测试内容",
            "type": "unknown_type",  # 不支持的类型
            "difficulty": 3,
            "answer_template": ["A", "B", "C"],
            "knowledge_point_id": 1
        }
        
        validator = QuestionFormatValidator()
        result, errors = validator.validate_questions([invalid_question])
        self.assertEqual(len(result), 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("不支持的题型", errors[0])


class QuestionFormatterTests(TestCase):
    """测试问题格式化功能"""
    
    def test_format_single_choice_question(self):
        """测试单选题格式化"""
        # 测试字符串形式的answer_template
        question_with_string = {
            "title": "测试题",
            "content": "内容",
            "type": "single_choice",
            "difficulty": 3,
            "answer_template": "选项A",
            "knowledge_point_id": 1
        }
        
        formatter = QuestionFormatter()
        formatted = formatter.format_questions([question_with_string])[0]
        self.assertIsInstance(formatted["answer_template"], list)
        self.assertEqual(formatted["answer_template"], ["选项A"])
        
        # 测试JSON字符串形式的answer_template
        question_with_json_string = {
            "title": "测试题",
            "content": "内容",
            "type": "single_choice",
            "difficulty": 3,
            "answer_template": '["选项A", "选项B", "选项C"]',
            "knowledge_point_id": 1
        }
        
        formatted = formatter.format_questions([question_with_json_string])[0]
        self.assertIsInstance(formatted["answer_template"], list)
        self.assertEqual(len(formatted["answer_template"]), 3)
        
        # 测试Python风格列表字符串
        question_with_python_list = {
            "title": "测试题",
            "content": "内容",
            "type": "single_choice",
            "difficulty": 3,
            "answer_template": "['选项A', '选项B', '选项C']",
            "knowledge_point_id": 1
        }
        
        formatted = formatter.format_questions([question_with_python_list])[0]
        self.assertIsInstance(formatted["answer_template"], list)
        
    def test_format_fill_blank_question(self):
        """测试填空题格式化"""
        # 测试没有填空标记的内容
        question_without_blank = {
            "title": "测试填空题",
            "content": "这里没有填空标记",
            "type": "fill_blank",
            "difficulty": 3,
            "answer_template": ["答案"],
            "knowledge_point_id": 1
        }
        
        formatter = QuestionFormatter()
        formatted = formatter.format_questions([question_without_blank])[0]
        self.assertIn("___", formatted["content"])  # 确认添加了填空标记
        
    def test_format_coding_question(self):
        """测试编程题格式化"""
        # 测试列表形式的answer_template
        question_with_list = {
            "title": "测试编程题",
            "content": "编写一个函数",
            "type": "coding",
            "difficulty": 3,
            "answer_template": ["def solution():", "    return True"],
            "knowledge_point_id": 1
        }
        
        formatter = QuestionFormatter()
        formatted = formatter.format_questions([question_with_list])[0]
        self.assertIsInstance(formatted["answer_template"], str)  # 确认转换为字符串
        self.assertIn("\n", formatted["answer_template"])  # 确认使用换行符连接
        
    def test_handle_formatting_errors(self):
        """测试处理格式化错误"""
        # 准备一个会导致格式化错误的问题
        problematic_question = {
            "title": "问题题目",
            "content": "内容",
            "type": "single_choice",
            # 假设这里的字典会导致错误
            "answer_template": {"key": "value"},
            "difficulty": 3,
            "knowledge_point_id": 1
        }
        
        formatter = QuestionFormatter()
        # 确认即使有错误，format_questions也不会抛出异常
        formatted = formatter.format_questions([problematic_question])
        self.assertEqual(len(formatted), 1)
        # 原始问题仍然被保留
        self.assertEqual(formatted[0]["answer_template"], {"key": "value"})


class IntegrationTests(TestCase):
    """集成测试验证和格式化流程"""
    
    def test_validate_then_format(self):
        """测试先验证再格式化的完整流程"""
        # 准备有效但格式需要调整的问题集合
        questions = [
            {
                "title": "单选题示例",
                "content": "这是单选题内容",
                "type": "single_choice",
                "difficulty": 3,
                "answer_template": '["选项A", "选项B", "选项C", "选项D"]',
                "knowledge_point_id": "1"  # 字符串形式，需要转换
            },
            {
                "title": "填空题示例",
                "content": "这是填空题，但没有填空标记",
                "type": "fill_blank",
                "difficulty": "2",  # 字符串形式，需要转换
                "answer_template": ["答案A", "答案B"],
                "knowledge_point_id": 2
            }
        ]
        
        # 先验证
        validator = QuestionFormatValidator()
        validated_questions, errors = validator.validate_questions(questions)
        
        # 验证应通过
        self.assertEqual(len(validated_questions), 2)
        self.assertEqual(len(errors), 0)
        
        # 再格式化
        formatter = QuestionFormatter()
        formatted_questions = formatter.format_questions(validated_questions)
        
        # 验证格式化结果
        self.assertEqual(len(formatted_questions), 2)
        
        # 检查单选题格式化结果
        self.assertIsInstance(formatted_questions[0]["answer_template"], list)
        self.assertEqual(len(formatted_questions[0]["answer_template"]), 4)
        self.assertIsInstance(formatted_questions[0]["knowledge_point_id"], int)
        
        # 检查填空题格式化结果
        self.assertIn("___", formatted_questions[1]["content"])  # 应添加填空标记
        self.assertIsInstance(formatted_questions[1]["difficulty"], int)  # 应转换为整数 