"""
提示模板模块测试

此文件包含对 a7/ai_services/services/n8n_webhook/prompt_templates.py 中
提示模板函数的单元测试。
"""
import pytest
from ..services.n8n_webhook.prompt_templates import (
    build_student_dialogue_prompt,
    build_question_generation_prompt,
    build_exercise_generation_prompt,
    build_answer_correction_prompt,
    build_course_content_generation_prompt,
    build_knowledge_to_markdown_prompt
)

class TestStudentDialoguePrompt:
    """测试学生对话提示模板函数"""

    def test_basic_query_only(self):
        """测试只有基本查询的情况"""
        query = "什么是人工智能？"
        prompt = build_student_dialogue_prompt(query)
        
        # 验证提示包含查询文本
        assert query in prompt
        # 验证提示包含指导文本
        assert "提供专业、准确、有帮助的回答" in prompt

    def test_with_previous_messages(self):
        """测试带有历史对话的情况"""
        query = "机器学习和深度学习有什么区别？"
        context = {
            "previous_messages": [
                {"role": "user", "content": "什么是人工智能？"},
                {"role": "assistant", "content": "人工智能是指通过程序使计算机模拟人类智能的技术..."}
            ]
        }
        
        prompt = build_student_dialogue_prompt(query, context)
        
        # 验证提示包含查询文本
        assert query in prompt
        # 验证提示包含历史对话
        assert "历史对话:" in prompt
        assert "人工智能是指通过程序" in prompt
        # 验证角色标识正确
        assert "学生:" in prompt
        assert "助手:" in prompt

    def test_with_additional_context(self):
        """测试带有其他上下文信息的情况"""
        query = "如何应用贝叶斯定理？"
        context = {
            "current_topic": "概率论",
            "learning_level": "大学二年级"
        }
        
        prompt = build_student_dialogue_prompt(query, context)
        
        # 验证提示包含上下文信息
        assert "current_topic: 概率论" in prompt
        assert "learning_level: 大学二年级" in prompt


class TestQuestionGenerationPrompt:
    """测试问题生成提示模板函数"""

    def test_basic_prompt_generation(self):
        """测试基本问题生成提示"""
        knowledge_point_ids = [1, 2]
        knowledge_points = [
            {"title": "线性代数基础", "content": "线性代数是研究向量空间的数学分支..."},
            {"title": "矩阵运算", "content": "矩阵是线性代数的核心概念..."}
        ]
        question_types = ["single_choice", "short_answer"]
        quantity = 5
        difficulty = 3
        
        prompt = build_question_generation_prompt(
            knowledge_point_ids,
            knowledge_points,
            question_types,
            quantity,
            difficulty
        )
        
        # 验证提示包含基本信息
        assert f"请生成{quantity}道题型为{', '.join(question_types)}" in prompt
        assert "中等" in prompt  # 难度级别
        
        # 验证知识点信息
        assert "知识点 1: 线性代数基础" in prompt
        assert "线性代数是研究向量空间的数学分支" in prompt
        assert "知识点 2: 矩阵运算" in prompt
        
        # 验证格式要求
        assert "```json" in prompt
        assert "title" in prompt
        assert "content" in prompt
        assert "type" in prompt


class TestExerciseGenerationPrompt:
    """测试练习题生成提示模板函数"""

    def test_complete_prompt(self):
        """测试完整参数的练习题生成提示"""
        query = "线性代数应用"
        knowledge_content = "线性代数是数学的一个分支，涉及向量空间、线性映射、矩阵等概念..."
        question_types = ["multiple_choice", "fill_blank"]
        quantity = 3
        difficulty = 4
        
        prompt = build_exercise_generation_prompt(
            query, 
            knowledge_content, 
            question_types, 
            quantity, 
            difficulty
        )
        
        # 验证提示包含所有参数
        assert f"生成{quantity}道练习题" in prompt
        assert query in prompt
        assert "基于以下知识点内容" in prompt
        assert knowledge_content in prompt
        assert f"题型要求: {', '.join(question_types)}" in prompt
        assert f"难度级别: {difficulty}/5" in prompt
        
        # 验证格式要求
        assert "```json" in prompt
        assert "title" in prompt
        assert "content" in prompt
        assert "type" in prompt
        assert "difficulty" in prompt

    def test_minimal_prompt(self):
        """测试最小参数的练习题生成提示"""
        query = "概率统计基础"
        quantity = 2
        
        prompt = build_exercise_generation_prompt(query, quantity=quantity)
        
        # 验证提示包含基本参数
        assert f"生成{quantity}道练习题" in prompt
        assert query in prompt
        
        # 验证不包含可选参数的说明部分
        assert "基于以下知识点内容" not in prompt
        assert "题型要求" not in prompt
        assert "难度级别: " not in prompt  # 注意这里添加了冒号和空格，只检查说明部分
        
        # 验证JSON模板中使用了"难度级别(可选)"而不是"难度级别(1-5)"
        assert "难度级别(可选)" in prompt
        assert "难度级别(1-5)" not in prompt


class TestAnswerCorrectionPrompt:
    """测试答案校正提示模板函数"""

    def test_choice_question_correction(self):
        """测试选择题答案校正提示"""
        exercise_content = "下列关于机器学习的描述，哪一项是正确的？"
        exercise_type = "single_choice"
        reference_answer = "B"
        student_answer = "C"
        answer_template = '["A. 机器学习不需要数据", "B. 机器学习是AI的一个子领域", "C. 机器学习只能用于图像识别", "D. 机器学习不能处理文本数据"]'
        
        prompt = build_answer_correction_prompt(
            exercise_content,
            exercise_type,
            reference_answer,
            student_answer,
            answer_template
        )
        
        # 验证提示内容
        assert "请评估以下选择题的答案正确性" in prompt
        assert exercise_content in prompt
        assert "选项：" in prompt
        assert reference_answer in prompt
        assert student_answer in prompt
        assert "JSON格式" in prompt
        assert "is_correct" in prompt
        assert "score" in prompt
        assert "feedback" in prompt

    def test_text_question_correction(self):
        """测试文本题答案校正提示"""
        exercise_content = "简述牛顿第二定律及其应用"
        exercise_type = "short_answer"
        reference_answer = "牛顿第二定律表明物体加速度与所受合外力成正比，与质量成反比..."
        student_answer = "牛顿第二定律是F=ma，表示力等于质量乘以加速度..."
        
        prompt = build_answer_correction_prompt(
            exercise_content,
            exercise_type,
            reference_answer,
            student_answer
        )
        
        # 验证提示内容
        assert "请评估以下题目的答案" in prompt
        assert f"题目类型：{exercise_type}" in prompt
        assert exercise_content in prompt
        assert reference_answer in prompt
        assert student_answer in prompt
        assert "JSON格式" in prompt


class TestCourseContentGenerationPrompt:
    """测试课程内容生成提示模板函数"""

    def test_complete_course_generation_prompt(self):
        """测试完整参数的课程内容生成提示"""
        course_name = "Python编程入门"
        chapter_count = 5
        course_description = "从零开始学习Python编程的基础课程"
        subject = "计算机科学"
        grade_level = "大学一年级"
        additional_requirements = "侧重实践案例，包含编程练习"
        
        prompt = build_course_content_generation_prompt(
            course_name,
            chapter_count,
            course_description,
            subject,
            grade_level,
            additional_requirements
        )
        
        # 验证提示内容
        assert f"请为一门名为'{course_name}'的{grade_level}{subject}课程生成内容大纲" in prompt
        assert f"要求包含{chapter_count}个主要知识点" in prompt
        assert f"课程描述：{course_description}" in prompt
        assert f"额外要求：{additional_requirements}" in prompt
        assert "JSON格式" in prompt

    def test_minimal_course_generation_prompt(self):
        """测试最小参数的课程内容生成提示"""
        course_name = "Web开发基础"
        chapter_count = 3
        course_description = "HTML, CSS和JavaScript入门"
        
        prompt = build_course_content_generation_prompt(
            course_name,
            chapter_count,
            course_description
        )
        
        # 验证提示内容
        assert f"请为一门名为'{course_name}'的" in prompt
        assert f"要求包含{chapter_count}个主要知识点" in prompt
        assert f"课程描述：{course_description}" in prompt
        assert "额外要求" not in prompt


class TestKnowledgeToMarkdownPrompt:
    """测试知识点转Markdown提示模板函数"""

    def test_knowledge_to_markdown_prompt(self):
        """测试知识点转Markdown提示"""
        knowledge_data = {
            "knowledge_points": [
                {"id": 1, "title": "Python基础", "content": "Python是一种高级编程语言..."}
            ],
            "courses": {
                "1": {"id": 1, "title": "编程入门", "subject": "计算机科学"}
            }
        }
        title = "Python编程教学"
        theme = "教学主题"
        
        prompt = build_knowledge_to_markdown_prompt(
            knowledge_data,
            title,
            theme,
            include_course_info=True
        )
        
        # 验证提示内容
        assert "适用于marp-cli的Markdown格式" in prompt
        assert f"演示标题为：{title}" in prompt
        assert f"使用主题：{theme}" in prompt
        assert "包含课程信息" in prompt
        assert "knowledge_points" in prompt 