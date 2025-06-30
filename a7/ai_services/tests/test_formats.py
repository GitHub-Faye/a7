"""
n8n Webhook 格式定义模块测试

此文件包含对 a7/ai_services/services/n8n_webhook/formats.py 中
Pydantic数据模型和辅助函数的单元测试。
"""
import pytest
from pydantic import ValidationError

from ..services.n8n_webhook.formats import (
    CourseGenerationRequestData,
    CourseGenerationResponseData,
    validate_request_data,
    parse_response,
)
from ..services.n8n_webhook.exceptions import (
    N8nInvalidRequestError,
    N8nResponseError,
)


class TestCourseGenerationRequestData:
    """测试 CourseGenerationRequestData 模型"""

    def test_successful_validation(self):
        """测试使用有效数据成功验证"""
        data = {
            "course_name": "线性代数入门",
            "chapter_count": 5,
            "course_description": "一门面向初学者的线性代数课程。",
            "subject": "数学",
            "grade_level": "大学",
            "additional_requirements": "需要微积分基础"
        }
        model = CourseGenerationRequestData(**data)
        assert model.course_name == data["course_name"]
        assert model.chapter_count == data["chapter_count"]

    def test_missing_required_field(self):
        """测试缺少必填字段时验证失败"""
        data = {
            # "course_name" 字段缺失
            "chapter_count": 5,
            "course_description": "一门面向初学者的线性代数课程。",
            "subject": "数学",
            "grade_level": "大学",
        }
        with pytest.raises(ValidationError):
            CourseGenerationRequestData(**data)

    def test_invalid_chapter_count(self):
        """测试 chapter_count 小于等于0时验证失败"""
        data = {
            "course_name": "线性代数入门",
            "chapter_count": 0,  # 无效值
            "course_description": "一门面向初学者的线性代数课程。",
            "subject": "数学",
            "grade_level": "大学",
        }
        with pytest.raises(ValidationError):
            CourseGenerationRequestData(**data)


class TestCourseGenerationResponseData:
    """测试 CourseGenerationResponseData 模型"""

    def test_successful_validation(self):
        """测试使用有效的嵌套数据成功验证"""
        data = {
            "course": {
                "title": "线性代数",
                "description": "课程描述",
                "subject": "数学",
                "grade_level": "大学"
            },
            "knowledge_points": [
                {
                    "title": "第一章：向量",
                    "content": "关于向量的介绍。",
                    "importance": 8,
                    "children": [
                        {
                            "title": "1.1 向量的定义",
                            "content": "什么是向量。",
                            "importance": 9,
                            "children": []
                        }
                    ]
                }
            ]
        }
        model = CourseGenerationResponseData.model_validate(data)
        assert model.course.title == "线性代数"
        assert len(model.knowledge_points) == 1
        assert model.knowledge_points[0].children[0].title == "1.1 向量的定义"

    def test_invalid_importance_field(self):
        """测试 importance 字段值超出范围时验证失败"""
        data = {
            "course": {"title": "标题", "description": "描述", "subject": "科目", "grade_level": "年级"},
            "knowledge_points": [
                {
                    "title": "章节一",
                    "content": "内容",
                    "importance": 11,  # 无效值
                    "children": []
                }
            ]
        }
        with pytest.raises(ValidationError):
            CourseGenerationResponseData.model_validate(data)

    def test_missing_nested_required_field(self):
        """测试嵌套对象中缺少必填字段时验证失败"""
        data = {
            "course": {"title": "标题", "description": "描述", "subject": "科目", "grade_level": "年级"},
            "knowledge_points": [
                {
                    # "title" 字段缺失
                    "content": "内容",
                    "importance": 8,
                    "children": []
                }
            ]
        }
        with pytest.raises(ValidationError):
            CourseGenerationResponseData.model_validate(data)


class TestHelperFunctions:
    """测试 formats.py 中的辅助函数"""

    def test_validate_request_data_success(self):
        """测试 validate_request_data 成功验证"""
        data = {
            "course_name": "课程", "chapter_count": 1, "course_description": "描述",
            "subject": "科目", "grade_level": "年级"
        }
        validated_model = validate_request_data("courseGeneration", data)
        assert isinstance(validated_model, CourseGenerationRequestData)
        assert validated_model.course_name == "课程"

    def test_validate_request_data_invalid_data(self):
        """测试 validate_request_data 因数据无效而引发异常"""
        data = {"course_name": "课程"}  # 缺少字段
        with pytest.raises(N8nInvalidRequestError) as excinfo:
            validate_request_data("courseGeneration", data)
        assert "验证失败" in str(excinfo.value)

    def test_validate_request_data_unknown_task_type(self):
        """测试 validate_request_data 因任务类型未知而引发异常"""
        with pytest.raises(N8nInvalidRequestError, match="不支持的任务类型: unknownTask"):
            validate_request_data("unknownTask", {})

    def test_parse_response_success(self):
        """测试 parse_response 成功解析"""
        data = {
            "course": {"title": "标题", "description": "描述", "subject": "科目", "grade_level": "年级"},
            "knowledge_points": [{"title": "章节", "content": "内容", "importance": 5}]
        }
        parsed_model = parse_response("courseGeneration", data)
        assert isinstance(parsed_model, CourseGenerationResponseData)
        assert parsed_model.course.title == "标题"

    def test_parse_response_invalid_data(self):
        """测试 parse_response 因数据无效而引发异常"""
        data = {"course": {"title": "标题"}}  # 缺少 knowledge_points
        with pytest.raises(N8nResponseError) as excinfo:
            parse_response("courseGeneration", data)
        assert "响应数据格式无效" in str(excinfo.value) 