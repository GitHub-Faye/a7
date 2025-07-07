"""
简单测试脚本，用于在Django环境之外测试marp命令
"""
import os
import subprocess
import tempfile
import sys

def test_marp_command():
    """测试marp命令是否可用"""
    # 使用两种方式尝试执行marp命令
    
    # 方式1: 直接使用marp命令
    try:
        print("尝试方式1: 直接使用marp命令")
        result = subprocess.run(
            "marp --version",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout.strip()}")
        print(f"标准错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"执行出错: {str(e)}")
    
    # 方式2: 使用完整路径
    try:
        print("\n尝试方式2: 使用完整路径")
        marp_cmd = "C:\\Users\\WYW\\AppData\\Roaming\\npm\\marp.cmd"
        result = subprocess.run(
            f"{marp_cmd} --version",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout.strip()}")
        print(f"标准错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"执行出错: {str(e)}")
    
    # 方式3: 使用npx
    try:
        print("\n尝试方式3: 使用npx")
        result = subprocess.run(
            "npx @marp-team/marp-cli --version",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout.strip()}")
        print(f"标准错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"执行出错: {str(e)}")
    
    # 测试创建一个简单的PDF
    print("\n测试创建PDF文件")
    try:
        # 创建临时Markdown文件
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("""---
marp: true
---

# 测试幻灯片

这是一个测试幻灯片
""")
            md_file = f.name
        
        # 创建临时输出文件
        pdf_file = os.path.join(tempfile.gettempdir(), "test_output.pdf")
        
        # 尝试使用方式2的命令（完整路径）生成PDF
        marp_cmd = "C:\\Users\\WYW\\AppData\\Roaming\\npm\\marp.cmd"
        cmd = f"{marp_cmd} {md_file} --pdf --output {pdf_file}"
        print(f"执行命令: {cmd}")
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout.strip()}")
        print(f"标准错误: {result.stderr.strip()}")
        
        # 检查文件是否生成
        if os.path.exists(pdf_file):
            print(f"PDF文件已生成: {pdf_file}")
            print(f"文件大小: {os.path.getsize(pdf_file)} 字节")
        else:
            print(f"PDF文件未生成: {pdf_file}")
        
        # 清理临时文件
        os.unlink(md_file)
        if os.path.exists(pdf_file):
            os.unlink(pdf_file)
            
    except Exception as e:
        print(f"执行出错: {str(e)}")
    
    # 打印环境变量
    print("\n当前环境变量PATH:")
    print(os.environ.get("PATH", "未设置"))

if __name__ == "__main__":
    test_marp_command() 