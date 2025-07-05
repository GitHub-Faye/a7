"""
问题导出模块

提供将AI生成的问题导出为不同格式(JSON, CSV)的功能。
"""

import json
import csv
import io
import logging
from typing import List, Dict, Any, Optional
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class QuestionExporter:
    """问题数据导出工具类，支持多种格式导出"""
    
    @staticmethod
    def export_as_json(questions: List[Dict[str, Any]], filename: Optional[str] = None) -> HttpResponse:
        """
        将问题数据导出为JSON格式
        
        Args:
            questions: 问题数据列表
            filename: 导出文件名，如不提供则使用默认文件名
            
        Returns:
            HttpResponse: 包含JSON数据的HTTP响应
        """
        if not filename:
            filename = "questions_export.json"
            
        # 确保文件名有正确的扩展名
        if not filename.lower().endswith('.json'):
            filename += '.json'
        
        # 准备JSON数据，使用缩进美化输出
        json_data = json.dumps(
            {"questions": questions}, 
            ensure_ascii=False, 
            indent=2
        )
        
        # 创建HTTP响应
        response = HttpResponse(
            json_data,
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_as_csv(questions: List[Dict[str, Any]], filename: Optional[str] = None) -> HttpResponse:
        """
        将问题数据导出为CSV格式
        
        Args:
            questions: 问题数据列表
            filename: 导出文件名，如不提供则使用默认文件名
            
        Returns:
            HttpResponse: 包含CSV数据的HTTP响应
        """
        if not filename:
            filename = "questions_export.csv"
            
        # 确保文件名有正确的扩展名
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        # 创建内存中的CSV文件
        csv_buffer = io.StringIO()
        
        # 确定CSV表头（字段名称）
        # 基础字段应该始终存在
        fieldnames = ['id', 'title', 'content', 'type', 'difficulty', 'knowledge_point_id', 'answer_template']
        
        # 创建CSV写入器
        writer = csv.DictWriter(
            csv_buffer,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL  # 对所有字段加引号，确保CSV格式正确
        )
        
        # 写入表头
        writer.writeheader()
        
        # 写入问题数据
        for i, question in enumerate(questions, 1):
            # 准备数据行
            row = {
                'id': i,  # 添加序号
                'title': question.get('title', ''),
                'content': question.get('content', ''),
                'type': question.get('type', ''),
                'difficulty': question.get('difficulty', ''),
                'knowledge_point_id': question.get('knowledge_point_id', ''),
            }
            
            # 特殊处理answer_template字段
            answer_template = question.get('answer_template', '')
            if isinstance(answer_template, list):
                # 将列表转换为JSON字符串
                row['answer_template'] = json.dumps(answer_template, ensure_ascii=False)
            else:
                row['answer_template'] = answer_template
                
            # 写入数据行
            writer.writerow(row)
        
        # 创建HTTP响应
        response = HttpResponse(
            csv_buffer.getvalue().encode('utf-8-sig'),  # 使用UTF-8 with BOM，确保Excel正确识别中文
            content_type='text/csv; charset=utf-8-sig'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_questions(questions: List[Dict[str, Any]], format_type: str, filename: Optional[str] = None) -> HttpResponse:
        """
        导出问题数据为指定格式
        
        Args:
            questions: 问题数据列表
            format_type: 导出格式，支持'json'和'csv'
            filename: 导出文件名，如不提供则使用默认文件名
            
        Returns:
            HttpResponse: 包含导出数据的HTTP响应
            
        Raises:
            ValueError: 如果指定了不支持的格式
        """
        format_type = format_type.lower()
        
        if format_type == 'json':
            return QuestionExporter.export_as_json(questions, filename)
        elif format_type == 'csv':
            return QuestionExporter.export_as_csv(questions, filename)
        else:
            raise ValueError(f"不支持的导出格式: {format_type}，目前支持的格式: json, csv") 