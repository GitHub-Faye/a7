import os
import pytest
import logging
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files import File

from courses.models import Course, KnowledgePoint
from courses.services.knowledge_to_ppt import KnowledgePointToPPTService

logger = logging.getLogger(__name__)

# 将此标记为跳过，除非特意要测试真实AI集成
# @pytest.mark.skip(reason="集成测试需要真实的AI服务，默认跳过")
class TestKnowledgePointToPPTIntegration(TestCase):
    """测试知识点到PPT转换与真实AI服务的集成"""

    def setUp(self):
        # 创建测试数据
        self.course = Course.objects.create(
            title="数学基础",
            subject="数学",
            grade_level="高中",
            description="高中数学基础概念与应用"
        )
        
        # 创建父知识点
        self.kp1 = KnowledgePoint.objects.create(
            title="函数与导数",
            content="函数与导数是微积分的基础概念，在数学建模中有广泛应用。",
            importance=5,
            course=self.course
        )
        
        # 创建子知识点
        self.kp1_1 = KnowledgePoint.objects.create(
            title="函数的概念",
            content="函数是描述一种对应关系的数学概念。若集合A中的任意一个元素x，都有唯一确定的集合B中的元素y与之对应，则称此对应为从集合A到集合B的函数。",
            importance=5,
            course=self.course,
            parent=self.kp1
        )
        
        self.kp1_2 = KnowledgePoint.objects.create(
            title="函数的性质",
            content="函数的基本性质包括单调性、奇偶性、周期性和有界性等。这些性质对理解函数行为至关重要。",
            importance=4,
            course=self.course,
            parent=self.kp1
        )
        
        self.kp1_3 = KnowledgePoint.objects.create(
            title="导数的概念",
            content="导数表示函数在某一点的变化率，是微积分的核心概念。导数定义为函数在某点的瞬时变化率。",
            importance=5,
            course=self.course,
            parent=self.kp1
        )
        
        # 创建服务实例
        self.service = KnowledgePointToPPTService()
        
    def test_real_ai_integration(self):
        """测试真实AI服务集成 - 生成Markdown并转换为PPT"""
        logger.info("开始真实AI集成测试")
        
        # 获取知识点数据
        knowledge_data = self.service.fetch_knowledge_points_hierarchy(
            [self.kp1.id], 
            include_children=True, 
            max_depth=3
        )
        
        # 记录知识点数据结构（部分）
        logger.info("知识点数据结构:")
        logger.info(f"- 知识点数量: {len(knowledge_data['knowledge_points'])}")
        logger.info(f"- 课程数量: {len(knowledge_data['courses'])}")
        for kp in knowledge_data['knowledge_points']:
            logger.info(f"- 知识点: {kp['id']} - {kp['title']}")
            if 'children' in kp:
                logger.info(f"  - 子知识点数量: {len(kp['children'])}")
        
        # 使用真实AI服务生成Markdown
        try:
            logger.info("正在调用AI服务生成Markdown...")
            
            markdown = self.service.generate_markdown_using_ai(
                knowledge_data, 
                title="函数与导数 - AI生成演示文稿", 
                include_course_info=True,
                theme="default"
            )
            
            logger.info(f"AI生成的Markdown长度: {len(markdown)}")
            logger.info("Markdown内容预览(前300字符):")
            logger.info(markdown[:300] + "...")
            
            # 验证生成的Markdown包含关键内容
            self.assertIn("函数与导数", markdown, "生成的Markdown中应包含知识点标题")
            self.assertIn("marp", markdown, "生成的Markdown应包含marp配置")
            
            # 验证是否包含分页符
            self.assertIn("---", markdown, "生成的Markdown应包含幻灯片分隔符")
            
            # 验证是否包含子知识点
            self.assertIn("函数的概念", markdown, "生成的Markdown应包含子知识点")
            self.assertIn("导数的概念", markdown, "生成的Markdown应包含子知识点")
            
            logger.info("Markdown内容验证通过，正在转换为PPTX...")
            
            # 转换为PPT并验证
            output_path, filename = self.service.validate_and_convert_markdown(
                markdown,
                format="pptx",
                theme="default"
            )
            
            # 验证文件是否存在
            full_path = os.path.join(settings.MEDIA_ROOT, output_path)
            self.assertTrue(os.path.exists(full_path), f"文件不存在: {full_path}")
            
            # 获取文件大小
            file_size = os.path.getsize(full_path)
            logger.info(f"生成的PPTX文件大小: {file_size} 字节")
            
            # 文件应该至少有一定大小
            self.assertGreater(file_size, 1000, "PPTX文件过小，可能生成失败")
            logger.info(f"生成的PPTX文件验证通过: {filename}")
            
            # 清理测试文件
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    logger.info(f"清理测试文件: {full_path}")
                except Exception as e:
                    logger.warning(f"清理测试文件失败: {e}")
            
        except Exception as e:
            logger.error(f"AI生成Markdown或转换过程失败: {str(e)}", exc_info=True)
            self.fail(f"AI生成Markdown或转换过程失败: {str(e)}")
    
    def test_complete_process_with_ai(self):
        """测试完整的知识点到PPT过程，使用AI服务"""
        logger.info("开始测试完整流程(AI模式)")
        
        try:
            # 调用完整处理流程
            result = self.service.process_knowledge_points_to_ppt({
                "knowledge_point_ids": [self.kp1.id],
                "include_children": True,
                "max_depth": 3,
                "format": "pptx",
                "use_ai": True,  # 启用AI模式
                "title": "函数与导数 - 完整流程测试"
            })
            
            logger.info(f"处理结果状态: {result['status']}")
            
            # 验证结果
            self.assertEqual(result["status"], "success", "处理应该成功")
            self.assertIn("file_url", result["data"], "结果应包含file_url")
            self.assertIn("filename", result["data"], "结果应包含filename")
            
            logger.info(f"生成的文件URL: {result['data']['file_url']}")
            
            # 验证文件是否存在
            file_url = result["data"]["file_url"]
            file_path = file_url.replace(settings.MEDIA_URL, "")
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            self.assertTrue(os.path.exists(full_path), f"文件不存在: {full_path}")
            
            # 获取文件大小
            file_size = os.path.getsize(full_path)
            logger.info(f"生成的PPTX文件大小: {file_size} 字节")
            
            # 文件应该至少有一定大小
            self.assertGreater(file_size, 10000, "PPTX文件过小，可能生成失败")
            logger.info("PPTX文件验证通过")
            
            # 清理测试文件
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    logger.info(f"清理测试文件: {full_path}")
                except Exception as e:
                    logger.warning(f"清理测试文件失败: {e}")
                    
        except Exception as e:
            logger.error(f"完整流程测试失败: {str(e)}", exc_info=True)
            self.fail(f"完整流程测试失败: {str(e)}") 