import logging
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple, Union

from django.conf import settings

from .exceptions import MarpCLIError
from .utils import OutputFormat, validate_output_format

# 创建日志记录器
logger = logging.getLogger(__name__)


class MarpCLIBuilder:
    """构建marp-cli命令行参数"""
    
    def __init__(self):
        """初始化CLI构建器"""
        self.args = []
        # 基本参数已添加
        self.has_format = False
        # 主题相关配置跟踪
        self.has_theme = False
        self.has_theme_dir = False
        self.has_style = False
    
    def add_input_file(self, file_path: str) -> 'MarpCLIBuilder':
        """
        添加输入文件路径
        
        Args:
            file_path: Markdown输入文件的路径
            
        Returns:
            更新后的构建器实例（链式调用）
        """
        if not os.path.exists(file_path):
            raise ValueError(f"输入文件不存在: {file_path}")
        
        self.args.append(file_path)
        return self
    
    def add_output_file(self, file_path: str) -> 'MarpCLIBuilder':
        """
        添加输出文件路径
        
        Args:
            file_path: 输出文件的路径
            
        Returns:
            更新后的构建器实例
        """
        self.args.extend(["--output", file_path])
        return self
    
    def set_format(self, output_format: str) -> 'MarpCLIBuilder':
        """
        设置输出格式
        
        Args:
            output_format: 输出格式（pdf, pptx, html, png）
            
        Returns:
            更新后的构建器实例
        """
        # 验证格式
        format_str = validate_output_format(output_format)
        
        # 避免重复添加格式参数
        if self.has_format:
            raise ValueError("输出格式已设置，不能重复设置")
        
        # 根据不同格式添加相应参数
        if format_str == OutputFormat.PDF:
            self.args.append("--pdf")
        elif format_str == OutputFormat.PPTX:
            self.args.append("--pptx")
        elif format_str == OutputFormat.HTML:
            self.args.append("--html")
        elif format_str == OutputFormat.PNG:
            self.args.extend(["--image", "png"])
        
        self.has_format = True
        return self
    
    def add_theme(self, theme: str) -> 'MarpCLIBuilder':
        """
        添加主题
        
        Args:
            theme: 主题名称
            
        Returns:
            更新后的构建器实例
        """
        if self.has_theme:
            raise ValueError("主题已设置，不能重复设置")
            
        self.args.extend(["--theme", theme])
        self.has_theme = True
        return self
    
    def add_theme_dir(self, theme_dir: str) -> 'MarpCLIBuilder':
        """
        添加自定义主题目录
        
        Args:
            theme_dir: 主题目录路径，包含自定义CSS文件
            
        Returns:
            更新后的构建器实例
        """
        if self.has_theme_dir:
            raise ValueError("主题目录已设置，不能重复设置")
            
        if not os.path.exists(theme_dir) or not os.path.isdir(theme_dir):
            raise ValueError(f"主题目录不存在或不是一个有效目录: {theme_dir}")
            
        self.args.extend(["--theme-set", theme_dir])
        self.has_theme_dir = True
        return self
    
    def add_style(self, css_path: str) -> 'MarpCLIBuilder':
        """
        添加额外样式表
        
        Args:
            css_path: CSS文件路径
            
        Returns:
            更新后的构建器实例
        """
        if not os.path.exists(css_path) or not css_path.endswith('.css'):
            raise ValueError(f"无效的CSS文件路径: {css_path}")
            
        self.args.extend(["--style", css_path])
        self.has_style = True
        return self
    
    def add_style_options(self, options: Dict[str, str]) -> 'MarpCLIBuilder':
        """
        添加样式选项，以CSS变量的形式注入
        
        Args:
            options: 样式选项字典，键为CSS变量名，值为CSS变量值
            
        Returns:
            更新后的构建器实例
        """
        if not options:
            return self
            
        # 创建内联样式表
        style_content = ":root {\n"
        for key, value in options.items():
            if not key.startswith("--"):
                key = f"--{key}"
            style_content += f"  {key}: {value};\n"
        style_content += "}"
        
        # 添加内联样式选项
        self.args.extend(["--style-css", style_content])
        return self
    
    def allow_local_files(self) -> 'MarpCLIBuilder':
        """
        允许访问本地文件
        
        Returns:
            更新后的构建器实例
        """
        self.args.append("--allow-local-files")
        return self
    
    def build(self) -> List[str]:
        """
        构建最终的命令行参数列表
        
        Returns:
            命令行参数列表
        """
        if not self.has_format:
            raise ValueError("必须设置输出格式")
        
        return self.args


class MarpCLIExecutor:
    """执行marp-cli命令"""
    
    def __init__(self, timeout: int = 60):
        """
        初始化执行器
        
        Args:
            timeout: 命令执行超时时间（秒）
        """
        self.timeout = timeout
        # 获取marp-cli路径，如果在Django设置中定义则使用，否则使用默认路径
        self.marp_command = getattr(settings, "MARP_CLI_PATH", "npx @marp-team/marp-cli")
        
        # 处理Windows环境下的命令
        if sys.platform == 'win32' and not self.marp_command.startswith("cmd /c"):
            self.marp_command = f"cmd /c {self.marp_command}"
    
    def execute(self, args: List[str]) -> Tuple[int, str, str]:
        """
        执行marp命令
        
        Args:
            args: 命令行参数列表
            
        Returns:
            (返回码, 标准输出, 标准错误)的元组
            
        Raises:
            MarpCLIError: 如果命令执行失败
        """
        # 构建完整命令
        if sys.platform == 'win32':
            # Windows环境下，确保命令是字符串形式
            if isinstance(self.marp_command, str):
                command_parts = self.marp_command.split()
                command = command_parts + args
            else:
                command = self.marp_command + args
        else:
            # Linux/Mac环境
            command = self.marp_command.split() + args
        
        try:
            logger.info(f"执行命令: {' '.join(command if isinstance(command, list) else [command])}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=isinstance(command, str)  # Windows下使用shell=True
            )
            
            stdout, stderr = process.communicate(timeout=self.timeout)
            returncode = process.returncode
            
            if returncode != 0:
                logger.error(f"命令执行失败，返回码: {returncode}, 错误: {stderr}")
                raise MarpCLIError(f"marp-cli执行失败，返回码: {returncode}, 错误: {stderr}")
            
            logger.info(f"命令执行成功，返回码: {returncode}")
            return returncode, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"命令执行超时: {self.timeout}秒")
            raise MarpCLIError(f"marp-cli执行超时: {self.timeout}秒")
        
        except FileNotFoundError:
            logger.error(f"找不到命令: {self.marp_command}")
            raise MarpCLIError(f"找不到marp-cli命令，请确保已安装: {self.marp_command}")
        
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
            raise MarpCLIError(f"执行marp-cli命令时出错: {e}") 