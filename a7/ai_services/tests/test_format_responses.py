"""
格式化响应功能的单元测试

此文件包含对 a7/ai_services/services/n8n_webhook/formats.py 中
各种响应格式化函数的单元测试。
"""

import pytest
from ..services.n8n_webhook.formats import (
    format_student_dialogue_response,
    format_question_generation_response,
    format_exercise_generation_response,
    format_answer_correction_response,
    format_course_generation_response
)


class TestStudentDialogueFormatting:
    """测试学生对话响应格式化"""

    def test_format_basic_dialogue_response(self):
        """测试基本对话响应格式化"""
        # 模拟统一格式的AI响应
        ai_response = {
            "answer": "神经网络是受人脑启发的计算模型，由多层互连的节点（神经元）组成。",
            "sources": "1. 深度学习基础, https://dl.example.com\n2. 人工智能导论"
        }
        
        # 格式化响应
        formatted = format_student_dialogue_response(ai_response)
        
        # 验证格式化结果
        assert "answer" in formatted
        assert formatted["answer"] == ai_response["answer"]
        assert "resources" in formatted
        assert "follow_up_questions" in formatted
        
        # 验证来源解析
        assert len(formatted["sources"]) == 2
        assert any(s["title"] == "深度学习基础" for s in formatted["sources"])
        assert any("url" in s and s["url"] == "https://dl.example.com" for s in formatted["sources"])

    def test_format_structured_dialogue_response(self):
        """测试包含结构化内容的对话响应格式化"""
        # 模拟包含结构化内容的AI响应
        ai_response = {
            "answer": """神经网络是受人脑启发的计算模型，由多层互连的节点（神经元）组成。

            参考资源:
            1. [深度学习基础](https://dl.example.com)
            2. [斯坦福CS229](https://cs229.stanford.edu)
            3. 机器学习：概念与实践
            
            后续问题:
            - 什么是激活函数？
            - 卷积神经网络如何工作？
            - 如何避免神经网络过拟合？""",
            "sources": ""  # 来源已包含在answer中
        }
        
        # 格式化响应
        formatted = format_student_dialogue_response(ai_response)
        
        # 验证格式化结果
        assert "answer" in formatted
        assert "神经网络是受人脑启发的计算模型" in formatted["answer"]
        assert "参考资源" not in formatted["answer"]  # 已被提取到resources
        assert "后续问题" not in formatted["answer"]  # 已被提取到follow_up_questions
        
        # 验证资源提取
        assert len(formatted["resources"]) == 3
        assert any("深度学习基础" in r["title"] for r in formatted["resources"])
        
        # 验证后续问题提取
        assert len(formatted["follow_up_questions"]) == 3
        assert "什么是激活函数？" in formatted["follow_up_questions"]
        assert "卷积神经网络如何工作？" in formatted["follow_up_questions"]

    def test_format_dialogue_with_json_content(self):
        """测试包含JSON内容的对话响应格式化"""
        # 模拟包含JSON内容的AI响应
        ai_response = {
            "answer": """以下是关于神经网络的基本信息:
            
            ```json
            {
              "title": "神经网络基础",
              "description": "神经网络是受人脑启发的计算模型",
              "components": ["输入层", "隐藏层", "输出层"],
              "common_types": ["前馈神经网络", "卷积神经网络", "循环神经网络"]
            }
            ```
            
            希望这些信息对您有帮助！""",
            "sources": "[机器学习导论](https://ml-intro.example.com)"
        }
        
        # 格式化响应
        formatted = format_student_dialogue_response(ai_response)
        
        # 验证格式化结果 - 应该提取JSON内容
        assert "answer" in formatted
        assert "title" in formatted["answer"]
        assert "components" in formatted["answer"]
        assert formatted["answer"]["title"] == "神经网络基础"
        assert "前馈神经网络" in formatted["answer"]["common_types"]
        
        # 验证来源解析
        assert len(formatted["sources"]) == 1
        assert formatted["sources"][0]["title"] == "机器学习导论"
        assert formatted["sources"][0]["url"] == "https://ml-intro.example.com"


class TestQuestionGenerationFormatting:
    """测试问题生成响应格式化"""

    def test_format_question_generation_response(self):
        """测试问题生成响应格式化"""
        # 模拟统一格式的AI响应
        ai_response = {
            "answer": """[
              {
                "title": "神经网络结构",
                "content": "神经网络的基本结构由哪三部分组成？",
                "type": "short_answer",
                "difficulty": 2,
                "answer": "输入层、隐藏层和输出层",
                "answer_template": "",
                "explanation": "神经网络的基本结构由输入层、一个或多个隐藏层以及输出层组成。"
              },
              {
                "title": "激活函数选择",
                "content": "以下哪个不是常用的激活函数？",
                "type": "multiple_choice",
                "difficulty": 3,
                "answer": "C",
                "answer_template": "A.ReLU B.Sigmoid C.Quadratic D.Tanh",
                "explanation": "二次函数(Quadratic)通常不用作激活函数，因为它不能解决消失梯度问题。"
              }
            ]""",
            "sources": ""
        }
        
        # 格式化响应
        formatted = format_question_generation_response(ai_response)
        
        # 验证格式化结果
        assert "questions" in formatted
        assert isinstance(formatted["questions"], list)
        assert len(formatted["questions"]) == 2
        
        # 验证第一个问题
        assert formatted["questions"][0]["title"] == "神经网络结构"
        assert formatted["questions"][0]["type"] == "short_answer"
        assert formatted["questions"][0]["difficulty"] == 2
        
        # 验证第二个问题
        assert formatted["questions"][1]["title"] == "激活函数选择"
        assert formatted["questions"][1]["type"] == "multiple_choice"
        assert formatted["questions"][1]["answer"] == "C"
        assert "Quadratic" in formatted["questions"][1]["answer_template"]


class TestAnswerCorrectionFormatting:
    """测试答案校正响应格式化"""

    def test_format_answer_correction_response(self):
        """测试答案校正响应格式化"""
        # 模拟统一格式的AI响应
        ai_response = {
            "answer": """{
              "is_correct": false,
              "score": 70,
              "feedback": "答案部分正确，但未完整描述神经网络的所有关键组件。",
              "improvement_suggestions": "可以增加对激活函数的描述，以及提及不同类型的神经网络架构。",
              "explanation": "一个完整的神经网络描述应包括输入层、隐藏层、输出层、激活函数、权重和偏置等组件。"
            }""",
            "sources": ""
        }
        
        # 格式化响应
        formatted = format_answer_correction_response(ai_response)
        
        # 验证格式化结果
        assert "is_correct" in formatted
        assert formatted["is_correct"] is False
        assert formatted["score"] == 70
        assert "feedback" in formatted
        assert "improvement_suggestions" in formatted
        assert "explanation" in formatted
        assert "激活函数" in formatted["improvement_suggestions"]

    def test_format_answer_correction_text_response(self):
        """测试文本格式的答案校正响应格式化"""
        # 模拟非JSON格式的AI响应
        ai_response = {
            "answer": """评估结果：不完全正确

            得分：65/100
            
            反馈：
            你的回答包含了神经网络的基本概念，但缺少对层次结构的清晰描述。
            
            改进建议：
            应该明确提及输入层、隐藏层和输出层的概念，以及它们各自的功能。
            
            解析：
            神经网络是由多层神经元组成的计算模型，包括输入层接收数据，隐藏层处理特征，输出层产生结果。""",
            "sources": ""
        }
        
        # 格式化响应
        formatted = format_answer_correction_response(ai_response)
        
        # 验证格式化结果
        assert "is_correct" in formatted
        assert formatted["is_correct"] is False  # 根据"不完全正确"判断
        assert formatted["score"] == 65
        assert "反馈" not in formatted["feedback"]  # 标题应被移除
        assert "神经网络的基本概念" in formatted["feedback"]
        assert "改进建议" not in formatted["improvement_suggestions"]  # 标题应被移除
        assert "输入层" in formatted["improvement_suggestions"]


class TestCourseGenerationFormatting:
    """测试课程生成响应格式化"""

    def test_format_course_generation_response(self):
        """测试课程生成响应格式化"""
        # 模拟统一格式的AI响应
        ai_response = {
            "answer": """{
              "course": {
                "name": "人工智能导论",
                "description": "面向初学者的AI入门课程",
                "subject": "计算机科学",
                "grade_level": "大学本科"
              },
              "knowledge_points": [
                {
                  "title": "人工智能基础",
                  "content": "人工智能的基本概念、历史和应用场景",
                  "importance": 9,
                  "children": [
                    {
                      "title": "人工智能的定义",
                      "content": "探讨不同视角下AI的定义及核心特征",
                      "importance": 8,
                      "children": []
                    },
                    {
                      "title": "人工智能发展历史",
                      "content": "从图灵测试到现代深度学习的发展历程",
                      "importance": 7,
                      "children": []
                    }
                  ]
                },
                {
                  "title": "机器学习基础",
                  "content": "机器学习的核心概念、算法和应用",
                  "importance": 10,
                  "children": []
                }
              ]
            }""",
            "sources": ""
        }
        
        # 格式化响应
        formatted = format_course_generation_response(ai_response)
        
        # 验证格式化结果
        assert "course" in formatted
        assert "knowledge_points" in formatted
        
        # 验证课程信息
        assert formatted["course"]["name"] == "人工智能导论"
        assert formatted["course"]["subject"] == "计算机科学"
        
        # 验证知识点结构
        assert len(formatted["knowledge_points"]) == 2
        assert formatted["knowledge_points"][0]["title"] == "人工智能基础"
        assert formatted["knowledge_points"][0]["importance"] == 9
        assert len(formatted["knowledge_points"][0]["children"]) == 2
        assert formatted["knowledge_points"][0]["children"][0]["title"] == "人工智能的定义"
        assert formatted["knowledge_points"][1]["title"] == "机器学习基础" 