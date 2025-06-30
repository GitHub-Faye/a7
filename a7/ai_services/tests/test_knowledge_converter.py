"""
知识点转换器模块测试

此文件包含对 a7/ai_services/services/knowledge_converter.py 中
数据转换函数的单元测试。
"""
import pytest
from django.db import IntegrityError

from courses.models import Course, KnowledgePoint
from users.models import User
from ..services.knowledge_converter import (
    convert_ai_response_to_knowledge_points,
    create_course_with_knowledge_points,
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

    def test_create_course_with_knowledge_points_success(self, teacher_user, valid_ai_response):
        """测试从AI响应成功创建课程和知识点"""
        course = create_course_with_knowledge_points(valid_ai_response, user=teacher_user)
        
        assert course is not None
        assert course.title == "量子物理"
        assert Course.objects.count() == 1
        
        # 验证知识点是否被正确创建并关联
        assert course.knowledge_points.filter(parent=None).count() == 2
        assert KnowledgePoint.objects.count() == 4   # 所有知识点

    def test_transaction_rolls_back_on_error(self, teacher_user, valid_ai_response):
        """测试在创建过程中发生错误时，事务是否能正确回滚"""
        # 修正：使用违反 NOT NULL 约束来触发 IntegrityError，这比 max_length 更可靠
        valid_ai_response["knowledge_points"][0]["children"][0]["title"] = None
        
        with pytest.raises(IntegrityError):
            create_course_with_knowledge_points(valid_ai_response, user=teacher_user)
            
        # 验证数据库中没有创建任何课程或知识点
        assert Course.objects.count() == 0
        assert KnowledgePoint.objects.count() == 0 