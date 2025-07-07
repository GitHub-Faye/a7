import os
import sys
from typing import Optional

from .cli import MarpCLIBuilder, MarpCLIExecutor
from .exceptions import MarpConversionError, MarpFileError, MarpServiceError
from .temp import MarpTempFileManager
from .utils import get_file_extension, validate_output_format


def convert_markdown_to_format(
    content: str,
    output_format: str,
    theme: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    将Markdown内容转换为指定格式。
    
    Args:
        content: Markdown内容
        output_format: 输出格式 ('pdf', 'pptx', 'html', 'png')
        theme: 可选的Marp主题名称
        output_path: 可选的输出文件路径，如果未提供则使用临时文件
        
    Returns:
        生成的文件路径
        
    Raises:
        MarpServiceError: 如果转换过程中发生错误
    """
    # 验证输出格式
    validate_output_format(output_format)
    
    # 创建临时文件管理器
    temp_manager = MarpTempFileManager()
    
    try:
        # 创建临时Markdown文件
        with temp_manager.create_temp_markdown_file(content) as input_file:
            # 确定输出路径
            if output_path:
                # 特殊处理Windows环境下的PNG输出
                if output_format.lower() == 'png' and sys.platform == 'win32' and os.path.isdir(output_path):
                    # 如果是目录，在Windows上需要指定具体文件名
                    file_path = os.path.join(output_path, "output.png")
                else:
                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    file_path = output_path
            else:
                # 使用临时输出路径
                extension = get_file_extension(output_format)
                file_path = temp_manager.get_temp_output_path('output', extension)
            
            # 构建命令行参数
            builder = MarpCLIBuilder()
            builder.add_input_file(input_file)
            builder.set_format(output_format)
            builder.add_output_file(file_path)
            builder.allow_local_files()
            
            # 添加主题（如果提供）
            if theme:
                builder.add_theme(theme)
                
            args = builder.build()
            
            # 执行命令
            executor = MarpCLIExecutor()
            executor.execute(args)
            
            # 确认输出文件已生成
            if not os.path.exists(file_path):
                raise MarpConversionError(f"转换失败，输出文件未生成: {file_path}")
            
            return file_path
    except Exception as e:
        # 确保清理临时文件
        temp_manager.cleanup()
        
        # 重新抛出适当的异常
        if isinstance(e, MarpServiceError):
            raise
        else:
            raise MarpConversionError(f"转换Markdown内容时出错: {e}")


def convert_file_to_format(
    file_path: str,
    output_format: str,
    theme: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    将Markdown文件转换为指定格式。
    
    Args:
        file_path: Markdown文件路径
        output_format: 输出格式 ('pdf', 'pptx', 'html', 'png')
        theme: 可选的Marp主题名称
        output_path: 可选的输出文件路径，如果未提供则使用临时文件
        
    Returns:
        生成的文件路径
        
    Raises:
        MarpServiceError: 如果转换过程中发生错误
    """
    # 验证输出格式
    validate_output_format(output_format)
    
    # 验证输入文件
    if not os.path.exists(file_path):
        raise MarpFileError(f"输入文件不存在: {file_path}")
    
    # 创建临时文件管理器（用于管理输出文件，如果未提供输出路径）
    temp_manager = MarpTempFileManager()
    
    try:
        # 确定输出路径
        if output_path:
            # 特殊处理Windows环境下的PNG输出
            if output_format.lower() == 'png' and sys.platform == 'win32' and os.path.isdir(output_path):
                # 如果是目录，在Windows上需要指定具体文件名
                output_file_path = os.path.join(output_path, "output.png")
            else:
                # 确保输出目录存在
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                output_file_path = output_path
        else:
            # 使用临时输出路径
            extension = get_file_extension(output_format)
            output_file_path = temp_manager.get_temp_output_path('output', extension)
        
        # 构建命令行参数
        builder = MarpCLIBuilder()
        builder.add_input_file(file_path)
        builder.set_format(output_format)
        builder.add_output_file(output_file_path)
        builder.allow_local_files()
        
        # 添加主题（如果提供）
        if theme:
            builder.add_theme(theme)
            
        args = builder.build()
        
        # 执行命令
        executor = MarpCLIExecutor()
        executor.execute(args)
        
        # 确认输出文件已生成
        if not os.path.exists(output_file_path):
            raise MarpConversionError(f"转换失败，输出文件未生成: {output_file_path}")
        
        return output_file_path
    except Exception as e:
        # 确保清理临时文件
        temp_manager.cleanup()
        
        # 重新抛出适当的异常
        if isinstance(e, MarpServiceError):
            raise
        else:
            raise MarpConversionError(f"转换Markdown文件时出错: {e}")
