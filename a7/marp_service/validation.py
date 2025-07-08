import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class MarkdownValidator:
    """Markdown验证器，用于验证和修复marp-cli格式的Markdown内容"""
    
    def __init__(self, content: str):
        self.content = content
        self.errors = []
        self.warnings = []
        self.slides = []
        self._parse_slides()
    
    def _parse_slides(self):
        """将Markdown内容解析为幻灯片列表"""
        # 清除之前的数据
        self.slides = []
        
        # 使用分隔符"---"分割幻灯片
        raw_slides = re.split(r'^---$', self.content, flags=re.MULTILINE)
        
        # 处理前置元数据（第一部分可能是前置元数据）
        if raw_slides and raw_slides[0].strip().startswith('---'):
            # 移除第一个元素的起始"---"
            raw_slides[0] = raw_slides[0][3:].strip()
        
        # 过滤空幻灯片并存储
        self.slides = [slide.strip() for slide in raw_slides if slide.strip()]
    
    def validate(self) -> bool:
        """执行全面验证，返回是否有效"""
        # 清除之前的错误和警告
        self.errors = []
        self.warnings = []
        
        # 重新解析内容以确保状态最新
        self._parse_slides()
        
        valid_frontmatter = self.validate_frontmatter()
        if not valid_frontmatter:
            return False
            
        valid_structure = self.validate_slides_structure()
        valid_hierarchy = self.validate_hierarchy()
        valid_syntax = self.validate_syntax()
        
        # 只有当没有错误时才返回True
        return len(self.errors) == 0
    
    def validate_frontmatter(self) -> bool:
        """验证前置元数据
        
        验证内容:
        1. 是否包含前置元数据区域
        2. 是否包含必要的marp配置
        """
        # 检查内容是否以"---"开头（前置元数据标记）
        if not self.content.strip().startswith("---"):
            self.errors.append("缺少前置元数据区域(---)")
            return False
        
        # 检查是否有至少一张幻灯片
        if not self.slides:
            self.errors.append("缺少前置元数据内容")
            return False
        
        # 获取第一个幻灯片内容（前置元数据）
        frontmatter = self.slides[0]
        
        # 检查必要的marp配置
        if not re.search(r'marp\s*:\s*true', frontmatter, re.IGNORECASE):
            self.errors.append("缺少必要的marp配置 'marp: true'")
            return False
            
        # 检查主题配置
        if not re.search(r'theme\s*:', frontmatter, re.IGNORECASE):
            self.warnings.append("缺少主题配置 'theme: [主题名]'")
        
        # 检查分页配置
        if not re.search(r'paginate\s*:', frontmatter, re.IGNORECASE):
            self.warnings.append("缺少分页配置 'paginate: true'")
            
        return True
    
    def validate_slides_structure(self) -> bool:
        """验证幻灯片结构
        
        验证内容:
        1. 是否有足够的幻灯片
        2. 是否有空白幻灯片
        3. 分隔符是否正确
        """
        # 检查幻灯片数量
        if len(self.slides) < 2:  # 至少需要前置元数据和标题页
            self.errors.append(f"幻灯片数量不足，当前仅有 {len(self.slides)} 张")
            return False
        
        # 检查空白幻灯片
        for i, slide in enumerate(self.slides):
            if not slide.strip():
                self.warnings.append(f"第 {i+1} 张幻灯片是空白的")
        
        # 检查分隔符格式
        separator_count = len(re.findall(r'^---$', self.content, flags=re.MULTILINE))
        expected_count = len(self.slides)
        
        if separator_count != expected_count:
            self.errors.append(f"幻灯片分隔符数量不正确，期望 {expected_count}，实际 {separator_count}")
            return False
            
        return True
    
    def validate_hierarchy(self) -> bool:
        """验证标题层级结构
        
        验证内容:
        1. 标题层级是否递增，不跳级
        2. 内容层级是否符合逻辑
        """
        # 跳过前置元数据幻灯片
        content_slides = self.slides[1:]
        
        if not content_slides:
            self.errors.append("缺少内容幻灯片")
            return False
            
        # 检查标题页
        first_slide = content_slides[0]
        if not re.search(r'^# ', first_slide, re.MULTILINE):
            self.warnings.append("第一张幻灯片缺少一级标题，应该是标题页")
        
        # 检查标题层级
        prev_level = 0
        hierarchy_errors = []
        
        for i, slide in enumerate(content_slides):
            # 提取所有标题
            headers = re.findall(r'^(#+) ', slide, re.MULTILINE)
            
            if not headers:
                continue
                
            # 检查当前幻灯片中的最高级标题
            min_level = min(len(h) for h in headers) if headers else 0
            
            # 检查是否跳级(多级跳跃)
            if min_level > 0 and prev_level > 0 and min_level > prev_level + 1:
                hierarchy_errors.append(f"标题层级跳跃: 从 {prev_level} 级跳到 {min_level} 级，在幻灯片 {i+2}")
            
            prev_level = min_level
        
        if hierarchy_errors:
            for error in hierarchy_errors:
                self.warnings.append(error)
        
        # 检查是否每个幻灯片都有内容
        for i, slide in enumerate(content_slides):
            headers = re.findall(r'^#+\s+(.+)$', slide, re.MULTILINE)
            content = re.sub(r'^#+\s+.+$', '', slide, flags=re.MULTILINE).strip()
            
            if headers and not content:
                self.warnings.append(f"幻灯片 {i+2} 只有标题没有内容")
        
        return True
    
    def validate_syntax(self) -> bool:
        """验证基本Markdown语法
        
        验证内容:
        1. 代码块是否闭合
        2. 列表格式是否正确
        """
        # 检查未闭合的代码块
        code_block_count = self.content.count("```")
        if code_block_count % 2 != 0:
            self.errors.append(f"存在未闭合的代码块: 共有 {code_block_count} 个标记，应为偶数")
            return False
        
        # 检查列表格式
        list_items = re.findall(r'^(\s*[-*+])\s', self.content, re.MULTILINE)
        mixed_markers = len(set(item.strip() for item in list_items)) > 1
        
        if mixed_markers:
            self.warnings.append("同一级别的列表使用了不同的标记符号，推荐统一使用 '-' 或 '*' 或 '+'")
        
        return True
    
    def get_issues(self) -> Dict[str, List[str]]:
        """获取验证过程中发现的问题"""
        return {
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def fix(self) -> str:
        """尝试修复发现的问题，返回修复后的内容"""
        # 初始化修复后的内容
        fixed_content = self.content
        
        # 1. 首先修复前置元数据（最重要的问题）
        if not fixed_content.strip().startswith("---") or "marp: true" not in fixed_content:
            fixed_content = self._fix_frontmatter(fixed_content)
        
        # 检查是否仍然缺少主题或分页配置
        if "theme:" not in fixed_content:
            fixed_content = self._add_missing_theme(fixed_content)
        
        if "paginate:" not in fixed_content:
            fixed_content = self._add_missing_paginate(fixed_content)
        
        # 2. 修复代码块问题
        code_block_count = fixed_content.count("```")
        if code_block_count % 2 != 0:
            fixed_content = self._fix_code_blocks(fixed_content)
        
        # 3. 修复幻灯片分隔符
        fixed_content = self._fix_slide_separators(fixed_content)
        
        # 4. 修复标题层级
        fixed_content = self._fix_hierarchy(fixed_content)
        
        # 5. 修复列表标记
        fixed_content = self._fix_list_markers(fixed_content)
        
        return fixed_content
    
    def _add_missing_theme(self, content: str) -> str:
        """添加缺失的theme配置"""
        frontmatter_match = re.search(r'^---\s*(.*?)\s*?^---', content, re.MULTILINE | re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1).strip()
            new_frontmatter = frontmatter + "\ntheme: default"
            return re.sub(r'^---\s*(.*?)\s*?^---', f"---\n{new_frontmatter}\n---", content, flags=re.MULTILINE | re.DOTALL)
        return content
    
    def _add_missing_paginate(self, content: str) -> str:
        """添加缺失的paginate配置"""
        frontmatter_match = re.search(r'^---\s*(.*?)\s*?^---', content, re.MULTILINE | re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1).strip()
            new_frontmatter = frontmatter + "\npaginate: true"
            return re.sub(r'^---\s*(.*?)\s*?^---', f"---\n{new_frontmatter}\n---", content, flags=re.MULTILINE | re.DOTALL)
        return content
    
    def _fix_frontmatter(self, content: str) -> str:
        """修复前置元数据"""
        # 如果内容不以"---"开头，添加完整的前置元数据
        if not content.strip().startswith("---"):
            basic_frontmatter = """---
marp: true
theme: default
paginate: true
---

"""
            return basic_frontmatter + content
        
        # 如果有前置元数据但格式不完整或缺少必要配置
        frontmatter_match = re.search(r'^---\s*(.*?)\s*?^---', content, re.MULTILINE | re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1).strip()
            new_frontmatter = frontmatter
            
            # 添加缺少的必要配置
            if not re.search(r'marp\s*:', new_frontmatter, re.IGNORECASE):
                new_frontmatter += "\nmarp: true"
            
            if not re.search(r'theme\s*:', new_frontmatter, re.IGNORECASE):
                new_frontmatter += "\ntheme: default"
            
            if not re.search(r'paginate\s*:', new_frontmatter, re.IGNORECASE):
                new_frontmatter += "\npaginate: true"
            
            # 更新前置元数据
            return re.sub(r'^---\s*(.*?)\s*?^---', f"---\n{new_frontmatter}\n---", content, flags=re.MULTILINE | re.DOTALL)
        
        return content
    
    def _fix_code_blocks(self, content: str) -> str:
        """修复未闭合的代码块"""
        # 计算需要添加的结束标记数量
        code_block_count = content.count("```")
        if code_block_count % 2 != 0:
            # 添加一个结束标记
            content = content + "\n```\n"
        
        return content
    
    def _fix_slide_separators(self, content: str) -> str:
        """修复幻灯片分隔符"""
        # 规范化幻灯片分隔符（确保每个分隔符前后都有空行）
        content = re.sub(r'([^\n])(\n---\n)', r'\1\n\n---\n\n', content)
        content = re.sub(r'(\n---\n)([^\n])', r'\n\n---\n\n\2', content)
        
        # 处理连续的分隔符（删除空白幻灯片）
        content = re.sub(r'\n---\n\s*\n---\n', r'\n---\n', content)
        
        # 删除结尾多余的分隔符
        content = re.sub(r'\n---\s*$', '', content)
        
        return content
    
    def _fix_hierarchy(self, content: str) -> str:
        """修复标题层级问题"""
        # 将内容分割为幻灯片
        slides = re.split(r'^---$', content, flags=re.MULTILINE)
        
        if len(slides) < 2:
            return content
            
        # 前置元数据不需要处理
        frontmatter = slides[0]
        content_slides = slides[1:]
        
        # 确保第一张幻灯片有一级标题
        if content_slides and not re.search(r'^# ', content_slides[0], re.MULTILINE):
            first_header = re.search(r'^(#+) (.+)$', content_slides[0], re.MULTILINE)
            if first_header:
                # 将标题提升为一级标题
                content_slides[0] = re.sub(
                    r'^#+\s+(.+)$', 
                    r'# \1', 
                    content_slides[0], 
                    count=1, 
                    flags=re.MULTILINE
                )
            elif content_slides[0].strip():
                # 如果没有标题但有内容，添加一个默认标题
                content_slides[0] = "# 标题\n\n" + content_slides[0]
        
        # 重建内容
        fixed_content = frontmatter
        for i, slide in enumerate(content_slides):
            fixed_content += "\n---\n" + slide
        
        return fixed_content
    
    def _fix_list_markers(self, content: str) -> str:
        """统一列表标记符号"""
        # 统一使用'-'作为列表标记
        content = re.sub(r'^(\s*)[*+](\s)', r'\1-\2', content, flags=re.MULTILINE)
        return content 