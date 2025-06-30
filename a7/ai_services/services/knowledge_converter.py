"""
知识点转换器模块

此模块提供将AI生成的课程内容（来自n8n）转换为内部数据库模型（Course, KnowledgePoint）的函数。
"""
from typing import Dict, List, Any
from django.db import transaction

from courses.models import Course, KnowledgePoint
from users.models import User

def convert_ai_response_to_knowledge_points(course: Course, response_data: Dict[str, Any]) -> List[KnowledgePoint]:
    """
    将AI生成的课程内容响应转换为知识点模型对象列表。
    
    Args:
        course: 知识点将关联到的课程对象。
        response_data: AI生成的响应数据，应包含一个 'knowledge_points' 键。
        
    Returns:
        创建的顶级知识点对象列表。
    """
    knowledge_points = []
    
    # 遍历响应中的每个顶级知识点数据
    for kp_data in response_data.get('knowledge_points', []):
        knowledge_point = _create_knowledge_point(course, kp_data)
        knowledge_points.append(knowledge_point)
        
    return knowledge_points

def _create_knowledge_point(course: Course, kp_data: Dict[str, Any], parent: KnowledgePoint = None) -> KnowledgePoint:
    """
    递归地创建一个知识点及其所有子知识点。
    
    Args:
        course: 知识点所属的课程。
        kp_data: 单个知识点的数据字典。
        parent: 父知识点对象（如果是子知识点）。
        
    Returns:
        创建的知识点对象。
    """
    # 创建知识点实例
    knowledge_point = KnowledgePoint(
        course=course,
        parent=parent,
        title=kp_data['title'],
        content=kp_data['content'],
        importance=kp_data.get('importance', 5)  # 如果未提供重要性，默认为5
    )
    knowledge_point.save()
    
    # 递归为子知识点创建实例
    for child_data in kp_data.get('children', []):
        _create_knowledge_point(course, child_data, parent=knowledge_point)
        
    return knowledge_point

@transaction.atomic
def create_course_with_knowledge_points(data: Dict[str, Any], user: User = None) -> Course:
    """
    在一个数据库事务中创建课程及其完整的知识点结构。
    
    Args:
        data: 包含课程信息和知识点结构的数据字典。
        user: 创建该课程的用户（教师）。
        
    Returns:
        创建的课程对象。
    """
    course_data = data.get('course', {})
    
    # 创建课程对象
    course = Course(
        title=course_data.get('title'),
        description=course_data.get('description'),
        subject=course_data.get('subject'),
        grade_level=course_data.get('grade_level'),
        teacher=user
    )
    course.save()
    
    # 使用转换函数创建知识点结构
    convert_ai_response_to_knowledge_points(course, data)
    
    return course 