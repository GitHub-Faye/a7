from enum import Enum
from typing import Dict, List, Optional, Union


class OutputFormat(str, Enum):
    """支持的输出格式枚举"""
    PDF = "pdf"
    PPTX = "pptx"
    HTML = "html"
    PNG = "png"


# 格式到MIME类型的映射
FORMAT_MIME_TYPES: Dict[str, str] = {
    OutputFormat.PDF: "application/pdf",
    OutputFormat.PPTX: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    OutputFormat.HTML: "text/html",
    OutputFormat.PNG: "image/png",
}

# 格式到文件扩展名的映射
FORMAT_EXTENSIONS: Dict[str, str] = {
    OutputFormat.PDF: ".pdf",
    OutputFormat.PPTX: ".pptx",
    OutputFormat.HTML: ".html",
    OutputFormat.PNG: ".png",
}

# 默认marp主题
DEFAULT_THEMES: List[str] = ["default", "gaia", "uncover"]


def validate_output_format(output_format: str) -> str:
    """
    验证输出格式是否受支持。
    
    Args:
        output_format: 要验证的输出格式字符串
        
    Returns:
        有效的输出格式字符串
        
    Raises:
        ValueError: 如果格式不受支持
    """
    try:
        return OutputFormat(output_format.lower())
    except ValueError:
        supported_formats = ", ".join([f.value for f in OutputFormat])
        raise ValueError(f"不支持的输出格式: {output_format}。支持的格式有: {supported_formats}")


def get_file_extension(output_format: str) -> str:
    """
    根据输出格式获取文件扩展名。
    
    Args:
        output_format: 输出格式字符串
        
    Returns:
        对应的文件扩展名
    """
    format_validated = validate_output_format(output_format)
    return FORMAT_EXTENSIONS[format_validated]


def get_mime_type(output_format: str) -> str:
    """
    根据输出格式获取MIME类型。
    
    Args:
        output_format: 输出格式字符串
        
    Returns:
        对应的MIME类型
    """
    format_validated = validate_output_format(output_format)
    return FORMAT_MIME_TYPES[format_validated] 