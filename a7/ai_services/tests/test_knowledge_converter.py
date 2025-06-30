"""
知识点转换器模块测试

此文件包含对 a7/ai_services/services/knowledge_converter.py 中
数据转换函数的单元测试。
"""
import pytest
import re
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from courses.models import Course, KnowledgePoint
from users.models import User
from ..services.knowledge_converter import (
    convert_ai_response_to_knowledge_points,
    create_course_with_knowledge_points,
    MAX_RECURSION_DEPTH,
)

# 标记所有测试都使用Django数据库
pytestmark = pytest.mark.django_db

@pytest.fixture
def teacher_user():
    """提供一个教师角色的用户实例"""
    user, _ = User.objects.get_or_create(username='teacher', defaults={'role': 'teacher'})
    return user

@pytest.fixture
def sample_course(teacher_user):
    """提供一个测试用的课程实例"""
    return Course.objects.create(
        title="基础物理学",
        description="一门基础物理课程",
        subject="物理",
        grade_level="高中",
        teacher=teacher_user
    )

@pytest.fixture
def valid_ai_response():
    """提供一个有效的、包含层级结构的AI响应数据"""
    return {
        "course": {
            "title": "量子物理",
            "description": "探索神奇的量子世界",
            "subject": "物理",
            "grade_level": "研究生"
        },
        "knowledge_points": [
            {
                "title": "第一章：波粒二象性",
                "content": "光的波粒二象性介绍。",
                "importance": 10,
                "children": [
                    {
                        "title": "1.1 光电效应",
                        "content": "解释光电效应的实验和理论。",
                        "importance": 9,
                        "children": []
                    },
                    {
                        "title": "1.2 康普顿散射",
                        "content": "康普顿散射实验。",
                        "importance": 8,
                        "children": []
                    }
                ]
            },
            {
                "title": "第二章：薛定谔方程",
                "content": "薛定谔方程及其解。",
                "importance": 9,
                "children": []
            }
        ]
    }
    
@pytest.fixture
def deep_ai_response():
    """创建一个深度超过最大限制的AI响应数据"""
    data = {"title": "Level 0", "content": "Content 0"}
    node = data
    for i in range(1, MAX_RECURSION_DEPTH + 5):
        child = {"title": f"Level {i}", "content": f"Content {i}", "children": []}
        node["children"] = [child]
        node = child
    return {"knowledge_points": [data]}

@pytest.fixture
def invalid_ai_response_missing_keys():
    """提供一个缺少'title'和'content'键的无效AI响应"""
    return {
        "course": {
            "title": "有效课程",
            "description": "有效描述",
            "subject": "有效主题",
            "grade_level": "有效年级"
        },
        "knowledge_points": [{"importance": 10}]
    }

@pytest.fixture
def invalid_ai_response_bad_structure():
    """提供一个结构错误的AI响应('children'不是列表)"""
    return {
        "knowledge_points": [
            {"title": "Valid", "content": "Valid Content", "children": {"not": "a list"}}
        ]
    }


class TestKnowledgeConverter:
    """测试知识点转换器函数"""

    def test_convert_ai_response_to_knowledge_points_success(self, sample_course, valid_ai_response):
        """测试成功将AI响应转换为知识点"""
        top_level_kps = convert_ai_response_to_knowledge_points(sample_course, valid_ai_response)
        
        assert len(top_level_kps) == 2
        assert KnowledgePoint.objects.count() == 4
        
        # 验证第一个顶级知识点及其子节点
        chapter1 = KnowledgePoint.objects.get(title="第一章：波粒二象性")
        assert chapter1.parent is None
        assert chapter1.children.count() == 2
        
        # 验证子知识点的父节点
        child1_1 = KnowledgePoint.objects.get(title="1.1 光电效应")
        assert child1_1.parent == chapter1

    def test_convert_with_empty_knowledge_points(self, sample_course):
        """测试当AI响应中知识点列表为空时的行为"""
        empty_response = {"knowledge_points": []}
        top_level_kps = convert_ai_response_to_knowledge_points(sample_course, empty_response)
        
        assert len(top_level_kps) == 0
        assert KnowledgePoint.objects.count() == 0
        
    def test_recursion_depth_limit(self, sample_course, deep_ai_response):
        """测试是否正确处理超过最大递归深度的场景"""
        with pytest.raises(ValueError, match="已达到最大递归深度"):
            convert_ai_response_to_knowledge_points(sample_course, deep_ai_response)
        
        # 验证只创建了达到最大深度的知识点
        assert KnowledgePoint.objects.count() == MAX_RECURSION_DEPTH + 1
        
    def test_invalid_data_missing_keys_raises_error(self, sample_course, invalid_ai_response_missing_keys):
        """测试当知识点数据缺少键时是否会引发ValueError"""
        expected_error = "知识点数据必须包含 'title' (不能为空) 和 'content' 字段。"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            convert_ai_response_to_knowledge_points(sample_course, invalid_ai_response_missing_keys)
        assert KnowledgePoint.objects.count() == 0

    def test_invalid_data_bad_structure_raises_error(self, sample_course, invalid_ai_response_bad_structure):
        """测试当'children'字段不是列表时是否会引发ValueError"""
        with pytest.raises(ValueError, match="知识点中的 'children' 必须是一个列表"):
            convert_ai_response_to_knowledge_points(sample_course, invalid_ai_response_bad_structure)
        assert KnowledgePoint.objects.count() == 1 # 父节点已创建

class TestCourseCreation:
    """测试包含知识点创建的整个课程创建流程"""

    def test_create_course_with_knowledge_points_success(self, teacher_user, valid_ai_response):
        """测试从AI响应成功创建课程和知识点"""
        course = create_course_with_knowledge_points(valid_ai_response, user=teacher_user)
        
        assert course is not None
        assert course.title == "量子物理"
        assert Course.objects.count() == 1
        
        # 验证知识点是否被正确创建并关联
        assert course.knowledge_points.filter(parent=None).count() == 2
        assert KnowledgePoint.objects.count() == 4   # 所有知识点

    def test_transaction_rolls_back_on_integrity_error(self, teacher_user, valid_ai_response):
        """测试在创建过程中发生数据库完整性错误时，事务是否能正确回滚"""
        # 使用违反 NOT NULL 约束来触发 IntegrityError
        valid_ai_response["knowledge_points"][0]["children"][0]["title"] = None
        
        expected_error = "知识点数据必须包含 'title' (不能为空) 和 'content' 字段。"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            create_course_with_knowledge_points(valid_ai_response, user=teacher_user)
            
        # 验证数据库中没有创建任何课程或知识点
        assert Course.objects.count() == 0
        assert KnowledgePoint.objects.count() == 0
        
    def test_transaction_rolls_back_on_validation_error(self, teacher_user, invalid_ai_response_missing_keys):
        """测试在创建过程中发生自定义验证错误时，事务是否能正确回滚"""
        expected_error = "知识点数据必须包含 'title' (不能为空) 和 'content' 字段。"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            create_course_with_knowledge_points(invalid_ai_response_missing_keys, user=teacher_user)
            
        # 验证数据库中没有创建任何课程或知识点
        assert Course.objects.count() == 0
        assert KnowledgePoint.objects.count() == 0
        
        # 测试课程数据无效的场景
        invalid_course_data = {"course": {"title": None}}
        with pytest.raises(ValueError, match="课程数据缺少必要的字段"):
             create_course_with_knowledge_points(invalid_course_data, user=teacher_user)

        assert Course.objects.count() == 0
        assert KnowledgePoint.objects.count() == 0 