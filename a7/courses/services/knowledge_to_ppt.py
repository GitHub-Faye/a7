import os
import uuid
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

from django.conf import settings
from django.db.models import Q
from django.core.files.storage import default_storage

from courses.models import KnowledgePoint, Course
from marp_service import convert_markdown_to_format
from marp_service.validation import MarkdownValidator
from ai_services.services.n8n_webhook.client import N8nWebhookClient

logger = logging.getLogger(__name__)

class KnowledgePointToPPTService:
    """
    知识点转PPT服务类
    负责获取知识点数据、生成Markdown和调用marp服务进行转换
    """
    
    def __init__(self):
        # 创建媒体文件存储目录
        self.presentation_dir = os.path.join('presentations')
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, self.presentation_dir)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, self.presentation_dir), exist_ok=True)
    
    def fetch_knowledge_points_hierarchy(
        self, 
        knowledge_point_ids: List[int], 
        include_children: bool = True, 
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        获取知识点及其子知识点的层级结构
        
        Args:
            knowledge_point_ids: 知识点ID列表
            include_children: 是否包含子知识点
            max_depth: 包含子知识点的最大深度
            
        Returns:
            包含知识点及其子知识点的字典
        """
        # 获取基本知识点
        base_knowledge_points = KnowledgePoint.objects.filter(
            id__in=knowledge_point_ids
        ).select_related('course')
        
        # 检查是否所有ID都找到了
        found_ids = {kp.id for kp in base_knowledge_points}
        missing_ids = set(knowledge_point_ids) - found_ids
        
        if missing_ids:
            logger.error(f"无法找到知识点: {missing_ids}")
            return {
                "error": "invalid_knowledge_points",
                "message": "部分知识点ID不存在",
                "details": [f"ID {id} 不存在" for id in missing_ids]
            }
        
        # 构建知识点层次结构
        result = {
            "knowledge_points": [],
            "courses": {}
        }
        
        # 处理每个知识点
        for kp in base_knowledge_points:
            course_id = kp.course.id
            if course_id not in result["courses"]:
                result["courses"][course_id] = {
                    "id": course_id,
                    "title": kp.course.title,
                    "subject": kp.course.subject,
                    "grade_level": kp.course.grade_level
                }
            
            # 添加知识点数据
            kp_data = self._build_knowledge_point_data(kp)
            
            # 如果需要，获取子知识点
            if include_children and max_depth > 0:
                children = self._get_child_knowledge_points(kp.id, max_depth)
                if children:
                    kp_data["children"] = children
            
            result["knowledge_points"].append(kp_data)
        
        return result
    
    def _build_knowledge_point_data(self, kp: KnowledgePoint) -> Dict[str, Any]:
        """构建知识点数据字典"""
        return {
            "id": kp.id,
            "title": kp.title,
            "content": kp.content,
            "course_id": kp.course.id,
            "importance": kp.importance
        }
    
    def _get_child_knowledge_points(self, parent_id: int, max_depth: int) -> List[Dict[str, Any]]:
        """递归获取子知识点"""
        if max_depth <= 0:
            return []
        
        children = KnowledgePoint.objects.filter(parent_id=parent_id).order_by('-importance')
        result = []
        
        for child in children:
            child_data = self._build_knowledge_point_data(child)
            
            # 递归获取下一级子知识点
            if max_depth > 1:
                grandchildren = self._get_child_knowledge_points(child.id, max_depth - 1)
                if grandchildren:
                    child_data["children"] = grandchildren
            
            result.append(child_data)
        
        return result
    
    def generate_markdown_from_knowledge_points(
        self, 
        knowledge_data: Dict[str, Any], 
        title: Optional[str] = None,
        include_course_info: bool = True
    ) -> str:
        """
        根据知识点数据生成Markdown
        
        Args:
            knowledge_data: 知识点数据字典
            title: 自定义演示标题
            include_course_info: 是否包含课程信息
            
        Returns:
            生成的Markdown字符串
        """
        md_lines = []
        
        # 添加marp指令
        md_lines.append("---")
        md_lines.append("marp: true")
        md_lines.append("theme: default")
        md_lines.append("paginate: true")
        md_lines.append("---")
        md_lines.append("")
        
        # 添加标题页
        if title:
            md_lines.append(f"# {title}")
        elif knowledge_data["knowledge_points"]:
            # 如果未提供标题，使用第一个知识点标题
            first_kp = knowledge_data["knowledge_points"][0]
            md_lines.append(f"# {first_kp['title']}")
            
            # 如果包含课程信息且存在课程
            if include_course_info and knowledge_data["courses"]:
                course_id = first_kp["course_id"]
                if course_id in knowledge_data["courses"]:
                    course = knowledge_data["courses"][course_id]
                    md_lines.append(f"## {course['title']} - {course['subject']} {course['grade_level']}")
        
        # 确保标题页有一些内容
        md_lines.append("知识点幻灯片")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # 处理每个知识点
        knowledge_points = knowledge_data.get("knowledge_points", [])
        if knowledge_points:
            for i, kp in enumerate(knowledge_points):
                # 如果不是第一个知识点，添加分隔符
                if i > 0:
                    md_lines.append("---")
                    md_lines.append("")
                
                self._add_knowledge_point_to_markdown(md_lines, kp, 1)
        else:
            # 至少添加一个空白内容页
            md_lines.append("## 无可用知识点")
            md_lines.append("")
            md_lines.append("请添加知识点内容")
        
        return "\n".join(md_lines)
    
    def _add_knowledge_point_to_markdown(self, md_lines: List[str], kp: Dict[str, Any], level: int):
        """递归添加知识点到Markdown中"""
        # 添加标题
        md_lines.append(f"{'#' * level} {kp['title']}")
        md_lines.append("")
        
        # 添加内容
        if kp['content']:
            # 简单格式化内容，实际可能需要更复杂的处理
            content_lines = kp['content'].split('\n')
            for line in content_lines:
                md_lines.append(line)
            
            md_lines.append("")
        else:
            # 确保即使没有内容也添加一些默认内容
            md_lines.append("暂无详细内容")
            md_lines.append("")
        
        # 不在每个知识点后添加分页符，而是在处理子知识点前添加
        
        # 处理子知识点
        if "children" in kp and kp["children"]:
            for i, child in enumerate(kp["children"]):
                # 为每个子知识点添加分页符
                if i > 0:
                    md_lines.append("---")
                    md_lines.append("")
                
                self._add_knowledge_point_to_markdown(md_lines, child, min(level + 1, 3))
    
    def validate_and_convert_markdown(self, markdown: str, format: str = 'pptx', theme: str = 'default') -> Tuple[str, str]:
        """
        验证Markdown并调用marp服务转换为演示文稿
        
        Args:
            markdown: Markdown内容
            format: 输出格式(pptx, pdf, html)
            theme: 主题名称
            
        Returns:
            元组 (文件路径, 文件名)
        """
        # 创建验证器对象
        validator = MarkdownValidator(markdown)
        
        # 执行验证
        is_valid = validator.validate()
        
        # 如果存在问题，尝试修复
        if not is_valid:
            issues = validator.get_issues()
            logger.warning(f"Markdown验证发现问题: {issues}")
            
            # 尝试修复问题
            markdown = validator.fix()
            logger.info("已尝试修复Markdown问题")
            
            # 再次验证修复后的内容
            validator = MarkdownValidator(markdown)
            if not validator.validate():
                logger.warning(f"修复后仍然存在问题: {validator.get_issues()}")
        
        # 生成唯一文件名
        unique_id = str(uuid.uuid4())
        output_filename = f"presentation_{unique_id}.{format}"
        output_path = os.path.join(self.presentation_dir, output_filename)
        
        # 创建完整的物理路径
        full_output_path = os.path.join(settings.MEDIA_ROOT, output_path)
        
        try:
            # 调用marp服务进行转换
            convert_markdown_to_format(
                content=markdown,
                output_format=format,
                output_path=full_output_path,
                theme=theme
            )
            
            # 返回相对路径和文件名，用于构建URL
            return output_path, output_filename
        
        except Exception as e:
            logger.error(f"Markdown转换失败: {str(e)}")
            raise ValueError(f"Markdown转换失败: {str(e)}")
    
    def generate_markdown_using_ai(
        self, 
        knowledge_data: Dict[str, Any], 
        title: Optional[str] = None,
        include_course_info: bool = True,
        theme: Optional[str] = None
    ) -> str:
        """
        使用AI服务根据知识点数据生成Markdown
        
        Args:
            knowledge_data: 知识点数据字典
            title: 自定义演示标题
            include_course_info: 是否包含课程信息
            theme: 演示主题名称
            
        Returns:
            生成的Markdown字符串
        """
        logger.info("使用AI服务生成Markdown")
        
        try:
            # 准备请求数据
            session_id = f"kp-to-md-{str(uuid.uuid4())}"
            
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
            
            # 创建客户端
            client = N8nWebhookClient()
            
            # 准备请求数据
            request_data = {
                "knowledge_data": knowledge_data,
                "title": title,
                "include_course_info": include_course_info,
                "theme": theme,
                "chatInput": prompt,
                "sessionId": session_id
            }
            
            logger.info("正在调用AI服务生成Markdown")
            
            # 调用AI服务
            response = client.generate_markdown_from_knowledge_sync(request_data)
            
            # 提取Markdown内容
            if response and "markdown" in response:
                markdown_content = response["markdown"]
                logger.info(f"AI成功生成Markdown，内容长度: {len(markdown_content)}")
                
                # 确保Markdown以marp前置元数据开头
                if not markdown_content.strip().startswith("---"):
                    logger.warning("AI生成的Markdown不包含marp前置元数据，添加默认配置")
                    marp_header = "---\nmarp: true\ntheme: default\npaginate: true\n---\n\n"
                    markdown_content = marp_header + markdown_content
                
                return markdown_content
            else:
                logger.error("AI响应缺少markdown字段")
                raise ValueError("AI生成Markdown失败: 响应缺少markdown字段")
                
        except Exception as e:
            logger.exception(f"使用AI生成Markdown时出错: {str(e)}")
            # 如果AI生成失败，回退到本地生成逻辑
            logger.info("回退到本地Markdown生成逻辑")
            return self.generate_markdown_from_knowledge_points(knowledge_data, title, include_course_info)
    
    def process_knowledge_points_to_ppt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识点到PPT的完整流程
        
        Args:
            data: 序列化器验证后的数据
            
        Returns:
            包含结果的字典
        """
        try:
            # 1. 获取知识点层次结构
            knowledge_data = self.fetch_knowledge_points_hierarchy(
                data["knowledge_point_ids"],
                data.get("include_children", True),
                data.get("max_depth", 3)
            )
            
            # 检查是否有错误
            if "error" in knowledge_data:
                return {
                    "status": "error",
                    "error": knowledge_data
                }
            
            # 2. 生成Markdown
            use_ai = data.get("use_ai", False)
            if use_ai:
                # 使用AI服务生成Markdown
                markdown_content = self.generate_markdown_using_ai(
                    knowledge_data,
                    data.get("title"),
                    data.get("include_course_info", True),
                    data.get("theme", "default")
                )
            else:
                # 使用本地逻辑生成Markdown
                markdown_content = self.generate_markdown_from_knowledge_points(
                    knowledge_data,
                    data.get("title"),
                    data.get("include_course_info", True)
                )
            
            # 3. 验证并转换Markdown
            output_path, filename = self.validate_and_convert_markdown(
                markdown_content,
                data.get("format", "pptx"),
                data.get("theme", "default")
            )
            
            # 4. 构建响应
            return {
                "status": "success",
                "data": {
                    "file_url": f"{settings.MEDIA_URL}{output_path}",
                    "filename": filename
                }
            }
            
        except Exception as e:
            logger.error(f"知识点转PPT处理失败: {str(e)}")
            return {
                "status": "error",
                "error": {
                    "code": "processing_error",
                    "message": f"处理失败: {str(e)}"
                }
            } 