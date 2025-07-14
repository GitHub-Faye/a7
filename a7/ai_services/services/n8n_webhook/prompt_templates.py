"""
提示模板模块

集中管理所有AI服务的提示模板，用于构建chatInput
"""

import json
from typing import Dict, Any, List, Optional, Union


def build_student_dialogue_prompt(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    构建学生对话提示
    
    Args:
        query: 学生的查询文本
        context: 可选的上下文信息，如历史对话
        
    Returns:
        str: 格式化的提示文本
    """
    prompt = f"学生问题: {query}\n\n"
    
    if context:
        # 添加历史对话上下文
        if "previous_messages" in context:
            prompt += "历史对话:\n"
            for msg in context["previous_messages"]:
                role = "学生" if msg.get("role") == "user" else "助手"
                prompt += f"{role}: {msg.get('content', '')}\n"
        
        # 添加其他上下文信息
        for key, value in context.items():
            if key != "previous_messages" and value:
                prompt += f"\n{key}: {value}\n"
    
    prompt += "\n请提供专业、准确、有帮助的回答，包括相关资源和后续问题建议。"
    return prompt


def build_question_generation_prompt(
    knowledge_point_ids: List[int], 
    knowledge_points: List[Dict[str, Any]], 
    question_types: List[str], 
    quantity: int, 
    difficulty: int = 3
) -> str:
    """
    构建问题生成提示
    
    Args:
        knowledge_point_ids: 知识点ID列表
        knowledge_points: 知识点详情列表
        question_types: 问题类型列表
        quantity: 生成问题数量
        difficulty: 难度级别(1-5)
        
    Returns:
        str: 格式化的提示文本
    """
    difficulty_text = {
        1: "简单", 
        2: "较简单", 
        3: "中等", 
        4: "较难", 
        5: "困难"
    }.get(difficulty, "中等")
    
    prompt = f"请生成{quantity}道题型为{', '.join(question_types)}的{difficulty_text}问题，基于以下知识点：\n\n"
    
    # 添加知识点信息
    for i, kp in enumerate(knowledge_points):
        kp_id = knowledge_point_ids[i] if i < len(knowledge_point_ids) else "未知"
        prompt += f"知识点 {kp_id}: {kp.get('title', '')}\n{kp.get('content', '')}\n\n"
    
    # 添加格式要求
    prompt += "\n请按以下JSON格式返回问题:\n"
    prompt += """
```json
[
  {
    "title": "问题标题",
    "content": "问题内容",
    "type": "问题类型",
    "difficulty": 难度级别(1-5),
    "answer": "参考答案",
    "answer_template": "答案模板或选项列表",
    "explanation": "解析说明"
  }
]
```
"""
    return prompt


def build_exercise_generation_prompt(query, knowledge_content=None, question_types=None, quantity=3, difficulty=None):
    """
    构建练习题生成提示
    
    Args:
        query: 查询文本或主题
        knowledge_content: 知识点内容（可选）
        question_types: 题型列表（可选）
        quantity: 题目数量（默认3）
        difficulty: 难度级别1-5（可选）
    
    Returns:
        str: 格式化的提示文本
    """
    prompt = f"生成{quantity}道练习题，内容关于: {query}\n\n"
    
    if knowledge_content:
        prompt += f"基于以下知识点内容：\n{knowledge_content}\n\n"
    
    if question_types:
        prompt += f"题型要求: {', '.join(question_types)}\n\n"
    
    if difficulty:
        prompt += f"难度级别: {difficulty}/5\n\n"
    
    # 根据是否提供了difficulty参数，调整JSON模板中的difficulty字段显示
    difficulty_template = f"难度级别(1-5)" if difficulty else "难度级别(可选)"
    
    prompt += f"""请按以下JSON格式返回练习题:

```json
[
  {{
    "title": "练习题标题",
    "content": "练习题内容",
    "type": "题型",
    "difficulty": {difficulty_template},
    "answer": "参考答案",
    "answer_template": "答案模板或选项列表"
  }}
]
```
"""
    return prompt


def build_answer_correction_prompt(
    exercise_content: str,
    exercise_type: str,
    reference_answer: str,
    student_answer: str,
    answer_template: Optional[str] = None
) -> str:
    """
    构建答案校正提示
    
    Args:
        exercise_content: 练习题内容
        exercise_type: 题目类型
        reference_answer: 参考答案
        student_answer: 学生答案
        answer_template: 答案模板或选项列表
        
    Returns:
        str: 格式化的提示文本
    """
    # 根据题型构建不同的提示
    if exercise_type in ["single_choice", "multiple_choice"]:
        prompt = (
            "请评估以下选择题的答案正确性：\n\n"
            f"题目：{exercise_content}\n\n"
        )
        
        if answer_template:
            prompt += f"选项：{answer_template}\n\n"
            
        prompt += (
            f"正确答案：{reference_answer}\n\n"
            f"学生答案：{student_answer}\n\n"
        )
    else:  # 简答题、填空题等
        prompt = (
            "请评估以下题目的答案：\n\n"
            f"题目类型：{exercise_type}\n"
            f"题目：{exercise_content}\n\n"
            f"参考答案：{reference_answer}\n\n"
            f"学生答案：{student_answer}\n\n"
        )
    
    prompt += """
请提供评估结果，按以下JSON格式返回:
```json
{
  "is_correct": true或false,
  "score": 0-100的分数,
  "feedback": "详细反馈",
  "improvement_suggestions": "改进建议",
  "explanation": "解析说明"
}
```
"""
    return prompt


def build_course_content_generation_prompt(
    course_name: str,
    chapter_count: int,
    course_description: str,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    additional_requirements: Optional[str] = None
) -> str:
    """
    构建课程内容生成提示
    
    Args:
        course_name: 课程名称
        chapter_count: 章节数量
        course_description: 课程描述
        subject: 学科
        grade_level: 年级水平
        additional_requirements: 额外要求
        
    Returns:
        str: 格式化的提示文本
    """
    subject_text = f"{subject}" if subject else ""
    grade_text = f"{grade_level}" if grade_level else ""
    
    prompt = (
        f"请为一门名为'{course_name}'的{grade_text}{subject_text}课程生成内容大纲，"
        f"要求包含{chapter_count}个主要知识点，每个知识点可以包含2-3个子知识点。\n\n"
        f"课程描述：{course_description}\n"
    )
    
    # 添加额外要求（如果有）
    if additional_requirements:
        prompt += f"\n额外要求：{additional_requirements}\n"
    
    # 添加格式要求
    prompt += """
请按以下JSON格式返回课程内容:
```json
{
  "course": {
    "name": "课程名称",
    "description": "课程描述",
    "subject": "学科",
    "grade_level": "年级水平"
  },
  "knowledge_points": [
    {
      "title": "知识点标题",
      "content": "知识点内容",
      "children": [
        {
          "title": "子知识点标题",
          "content": "子知识点内容"
        }
      ]
    }
  ]
}
```
"""
    return prompt


def build_knowledge_to_markdown_prompt(
    knowledge_data: Dict[str, Any],
    title: Optional[str] = None,
    theme: Optional[str] = None,
    include_course_info: bool = True
) -> str:
    """
    构建知识点转Markdown提示
    
    Args:
        knowledge_data: 知识点数据
        title: 演示标题
        theme: 演示主题
        include_course_info: 是否包含课程信息
        
    Returns:
        str: 格式化的提示文本
    """
    # 将知识点数据转换为可读的JSON字符串
    knowledge_json = json.dumps(knowledge_data, ensure_ascii=False, indent=2)
    
    # 构建提示文本
    prompt = "请将以下知识点数据转换为适用于marp-cli的Markdown格式，保持层级结构。"
    
    if title:
        prompt += f" 演示标题为：{title}。"
        
    if theme:
        prompt += f" 使用主题：{theme}。"
        
    if include_course_info:
        prompt += " 包含课程信息。"
    else:
        prompt += " 不需要包含课程信息。"
        
    prompt += "\n\n知识点数据如下：\n```json\n" + knowledge_json + "\n```"
    
    # 生成Markdown的要求
    prompt += "\n\n生成的Markdown应满足以下要求："
    prompt += "\n1. 符合marp-cli的语法，以---分隔幻灯片"
    prompt += "\n2. 以marp前置元数据开头，包含marp: true, theme: default, paginate: true等配置"
    prompt += "\n3. 保持知识点的层级结构，标题级别反映层级关系"
    prompt += "\n4. 第一张幻灯片为标题页，包含演示标题"
    prompt += "\n5. 每个知识点应有独立的幻灯片"
    prompt += "\n6. 给每张幻灯片添加适当的格式，如标题、正文、列表等"
    
    return prompt 