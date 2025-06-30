"""
知识点转换器模块

此模块提供将AI生成的课程内容（来自n8n）转换为内部数据库模型（Course, KnowledgePoint）的函数。
"""
import logging
from typing import Dict, List, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from courses.models import Course, KnowledgePoint
from users.models import User

# 获取日志记录器
logger = logging.getLogger(__name__)

# 定义递归最大深度，防止无限递归
MAX_RECURSION_DEPTH = 10

def convert_ai_response_to_knowledge_points(
    course: Course, 
    response_data: Dict[str, Any]
) -> List[KnowledgePoint]:
    """
    将AI生成的课程内容响应转换为知识点模型对象列表。
    
    Args:
        course: 知识点将关联到的课程对象。
        response_data: AI生成的响应数据，应包含一个 'knowledge_points' 键。
        
    Returns:
        创建的顶级知识点对象列表。
        
    Raises:
        ValueError: 如果响应数据结构无效。
    """
    knowledge_points_data = response_data.get('knowledge_points')
    if knowledge_points_data is None:
        logger.warning("AI响应中缺少 'knowledge_points' 键。")
        return []

    if not isinstance(knowledge_points_data, list):
        raise ValueError("AI响应中的 'knowledge_points' 必须是一个列表。")

    created_knowledge_points = []
    for kp_data in knowledge_points_data:
        # 调用递归函数创建知识点
        knowledge_point = _create_knowledge_point_recursive(course, kp_data)
        created_knowledge_points.append(knowledge_point)
        
    return created_knowledge_points

def _create_knowledge_point_recursive(
    course: Course, 
    kp_data: Dict[str, Any], 
    parent: KnowledgePoint = None,
    current_depth: int = 0
) -> KnowledgePoint:
    """
    递归地创建一个知识点及其所有子知识点，并进行验证。
    
    Args:
        course: 知识点所属的课程。
        kp_data: 单个知识点的数据字典。
        parent: 父知识点对象（如果是子知识点）。
        current_depth: 当前递归深度。
        
    Returns:
        创建的知识点对象。
        
    Raises:
        ValueError: 如果数据格式无效或达到最大递归深度。
    """
    # 检查递归深度
    if current_depth > MAX_RECURSION_DEPTH:
        error_msg = f"已达到最大递归深度 ({MAX_RECURSION_DEPTH})。知识点 '{kp_data.get('title', 'N/A')}' 的子节点将不会被创建。"
        logger.warning(error_msg)
        raise ValueError(error_msg)

    # 验证关键字段是否存在
    if 'title' not in kp_data or not kp_data['title'] or 'content' not in kp_data:
        raise ValueError("知识点数据必须包含 'title' (不能为空) 和 'content' 字段。")

    # 创建知识点实例
    try:
        knowledge_point = KnowledgePoint(
            course=course,
            parent=parent,
            title=str(kp_data['title']).strip(),  # 清理标题
            content=kp_data['content'],
            importance=kp_data.get('importance', 5)
        )
        knowledge_point.full_clean()  # 运行模型级别的验证
        knowledge_point.save()
    except (ValidationError, TypeError, KeyError) as e:
        logger.error(f"创建知识点 '{kp_data.get('title')}' 失败: {e}")
        raise ValueError(f"知识点数据验证失败: {e}") from e

    # 递归为子知识点创建实例
    children_data = kp_data.get('children', [])
    if not isinstance(children_data, list):
        raise ValueError("知识点中的 'children' 必须是一个列表。")
        
    for child_data in children_data:
        _create_knowledge_point_recursive(
            course, 
            child_data, 
            parent=knowledge_point, 
            current_depth=current_depth + 1
        )
        
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
        
    Raises:
        ValueError: 如果输入数据验证失败。
        Exception: 其他数据库或未知错误。
    """
    course_data = data.get('course', {})
    if not isinstance(course_data, dict):
        raise ValueError("请求数据中的 'course' 字段必须是一个字典。")
        
    # 验证课程数据
    if not all(k in course_data for k in ['title', 'description', 'subject', 'grade_level']):
        raise ValueError("课程数据缺少必要的字段（title, description, subject, grade_level）。")

    logger.info(f"开始为用户 '{user.username if user else 'N/A'}' 创建课程 '{course_data.get('title')}'...")

    try:
        # 创建课程对象
        course = Course(
            title=course_data.get('title'),
            description=course_data.get('description'),
            subject=course_data.get('subject'),
            grade_level=course_data.get('grade_level'),
            teacher=user
        )
        course.full_clean()
        course.save()
        
        # 使用转换函数创建知识点结构
        convert_ai_response_to_knowledge_points(course, data)
        
        logger.info(f"课程 '{course.title}' (ID: {course.id}) 及其知识点已成功创建。")
        return course

    except (ValueError, ValidationError) as e:
        logger.error(f"创建课程失败，事务已回滚: {e}")
        # 重新抛出异常以确保事务管理器能够捕获
        raise
    except Exception as e:
        logger.exception(f"创建课程时发生未知错误，事务已回滚: {e}")
        # 重新抛出以确保上层可以捕获
        raise 