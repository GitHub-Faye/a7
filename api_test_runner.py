#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识点到PPT直接下载API端到端测试脚本
测试真实环境中API的功能和性能
"""

import os
import sys
import time
import json
import requests
import argparse
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('api_test')

class APITester:
    """API测试工具类"""
    
    def __init__(self, base_url, token=None):
        """
        初始化测试工具
        
        参数:
        - base_url: API基础URL
        - token: 认证令牌（可选）
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        
        # 如果提供了token，设置认证头
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            
        # 设置通用头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # 创建输出目录
        self.output_dir = 'api_test_output'
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"API测试工具初始化完成，基础URL: {base_url}")
    
    def test_knowledge_to_ppt_direct_download(self, knowledge_point_ids, format='pptx', include_children=True):
        """
        测试知识点到PPT的直接下载功能
        
        参数:
        - knowledge_point_ids: 知识点ID列表
        - format: 输出格式，可选值: pptx, pdf, html
        - include_children: 是否包含子知识点
        
        返回:
        - 测试结果字典
        """
        endpoint = f"{self.base_url}/api/knowledge-points-to-ppt/"
        
        # 准备请求数据
        data = {
            "knowledge_point_ids": knowledge_point_ids,
            "format": format,
            "include_children": include_children,
            "direct_download": True,
            "filename": f"test_download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        logger.info(f"测试知识点到PPT直接下载API，知识点IDs: {knowledge_point_ids}, 格式: {format}")
        
        try:
            # 测量响应时间
            start_time = time.time()
            response = self.session.post(endpoint, json=data, stream=True)
            response_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code == 200:
                # 获取文件名
                content_disposition = response.headers.get('Content-Disposition', '')
                filename = None
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    filename = f"downloaded_{format}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}"
                
                # 保存文件
                file_path = os.path.join(self.output_dir, filename)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(file_path)
                
                logger.info(f"下载成功，文件保存为: {file_path}")
                logger.info(f"文件大小: {file_size} 字节")
                logger.info(f"响应时间: {response_time:.2f} 秒")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "file_path": file_path,
                    "file_size": file_size,
                    "content_type": response.headers.get('Content-Type'),
                    "filename": filename
                }
            else:
                # 处理错误响应
                try:
                    error_data = response.json()
                    logger.error(f"API请求失败: {response.status_code}, 错误: {json.dumps(error_data, ensure_ascii=False)}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "error": error_data
                    }
                except:
                    logger.error(f"API请求失败: {response.status_code}, 响应内容: {response.text}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "error": response.text
                    }
                    
        except Exception as e:
            logger.error(f"测试过程中发生异常: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_knowledge_to_ppt_base64_content(self, knowledge_point_ids, format='pptx'):
        """
        测试知识点到PPT返回Base64编码内容功能
        
        参数:
        - knowledge_point_ids: 知识点ID列表
        - format: 输出格式，可选值: pptx, pdf, html
        
        返回:
        - 测试结果字典
        """
        endpoint = f"{self.base_url}/api/knowledge-points-to-ppt/"
        
        # 准备请求数据
        data = {
            "knowledge_point_ids": knowledge_point_ids,
            "format": format,
            "return_file_content": True
        }
        
        logger.info(f"测试知识点到PPT返回Base64内容，知识点IDs: {knowledge_point_ids}, 格式: {format}")
        
        try:
            # 测量响应时间
            start_time = time.time()
            response = self.session.post(endpoint, json=data)
            response_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code == 200:
                response_data = response.json()
                
                # 验证响应格式
                if response_data.get("status") == "success" and "data" in response_data:
                    data = response_data["data"]
                    
                    # 检查是否包含Base64编码的文件内容
                    if "file_content" in data:
                        # 保存文件
                        filename = data.get("filename", f"base64_content_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}")
                        file_path = os.path.join(self.output_dir, filename)
                        
                        # 解码并保存文件
                        import base64
                        with open(file_path, 'wb') as f:
                            f.write(base64.b64decode(data["file_content"]))
                        
                        file_size = os.path.getsize(file_path)
                        
                        logger.info(f"Base64内容解码并保存为: {file_path}")
                        logger.info(f"文件大小: {file_size} 字节")
                        logger.info(f"响应时间: {response_time:.2f} 秒")
                        
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "response_time": response_time,
                            "file_path": file_path,
                            "file_size": file_size,
                            "filename": filename
                        }
                    else:
                        logger.error("响应中缺少file_content字段")
                        return {
                            "success": False,
                            "status_code": response.status_code,
                            "response_time": response_time,
                            "error": "响应中缺少file_content字段",
                            "response_data": response_data
                        }
                else:
                    logger.error(f"响应格式不符合预期: {json.dumps(response_data, ensure_ascii=False)}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "error": "响应格式不符合预期",
                        "response_data": response_data
                    }
            else:
                # 处理错误响应
                try:
                    error_data = response.json()
                    logger.error(f"API请求失败: {response.status_code}, 错误: {json.dumps(error_data, ensure_ascii=False)}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "error": error_data
                    }
                except:
                    logger.error(f"API请求失败: {response.status_code}, 响应内容: {response.text}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "error": response.text
                    }
                    
        except Exception as e:
            logger.error(f"测试过程中发生异常: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self, knowledge_point_ids):
        """
        运行所有测试
        
        参数:
        - knowledge_point_ids: 知识点ID列表
        
        返回:
        - 测试结果字典
        """
        results = {}
        
        # 测试不同格式的直接下载
        for format in ['pptx', 'pdf', 'html']:
            test_name = f"direct_download_{format}"
            logger.info(f"运行测试: {test_name}")
            results[test_name] = self.test_knowledge_to_ppt_direct_download(
                knowledge_point_ids, 
                format=format
            )
        
        # 测试Base64内容返回
        for format in ['pptx', 'pdf']:
            test_name = f"base64_content_{format}"
            logger.info(f"运行测试: {test_name}")
            results[test_name] = self.test_knowledge_to_ppt_base64_content(
                knowledge_point_ids, 
                format=format
            )
        
        # 生成测试报告
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results):
        """
        生成测试报告
        
        参数:
        - results: 测试结果字典
        """
        report_path = os.path.join(self.output_dir, f"test_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html")
        
        # 计算成功率
        total_tests = len(results)
        successful_tests = sum(1 for result in results.values() if result.get("success", False))
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 生成HTML报告
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API测试报告</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .summary {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .success {{
                    color: #28a745;
                }}
                .failure {{
                    color: #dc3545;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    padding: 12px 15px;
                    border: 1px solid #ddd;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f8f8;
                }}
                .test-details {{
                    margin-bottom: 30px;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>知识点到PPT API测试报告</h1>
                <div class="summary">
                    <h2>测试摘要</h2>
                    <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>测试总数: {total_tests}</p>
                    <p>成功测试: <span class="success">{successful_tests}</span></p>
                    <p>失败测试: <span class="failure">{total_tests - successful_tests}</span></p>
                    <p>成功率: <strong>{success_rate:.2f}%</strong></p>
                </div>
                
                <h2>测试结果详情</h2>
        """
        
        # 添加每个测试的详情
        for test_name, result in results.items():
            success = result.get("success", False)
            status_class = "success" if success else "failure"
            status_text = "成功" if success else "失败"
            
            html += f"""
                <div class="test-details">
                    <h3>{test_name} - <span class="{status_class}">{status_text}</span></h3>
                    <table>
                        <tr>
                            <th>属性</th>
                            <th>值</th>
                        </tr>
            """
            
            # 添加测试结果的属性
            for key, value in result.items():
                if key not in ["error", "response_data"] and not isinstance(value, dict):
                    html += f"""
                        <tr>
                            <td>{key}</td>
                            <td>{value}</td>
                        </tr>
                    """
            
            html += """
                    </table>
            """
            
            # 添加错误信息（如果有）
            if "error" in result and result["error"]:
                html += f"""
                    <h4>错误信息:</h4>
                    <pre>{json.dumps(result["error"], ensure_ascii=False, indent=2)}</pre>
                """
            
            # 添加响应数据（如果有）
            if "response_data" in result and result["response_data"]:
                html += f"""
                    <h4>响应数据:</h4>
                    <pre>{json.dumps(result["response_data"], ensure_ascii=False, indent=2)}</pre>
                """
            
            html += """
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        # 写入HTML报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"测试报告已生成: {report_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='知识点到PPT API端到端测试工具')
    parser.add_argument('--url', type=str, default='http://localhost:8000',
                        help='API基础URL (默认: http://localhost:8000)')
    parser.add_argument('--token', type=str, help='认证令牌（可选）')
    parser.add_argument('--knowledge-ids', type=str, required=True,
                        help='知识点ID列表，用逗号分隔，例如: "1,2,3"')
    
    args = parser.parse_args()
    
    # 解析知识点ID列表
    try:
        knowledge_point_ids = [int(id.strip()) for id in args.knowledge_ids.split(',')]
    except ValueError:
        logger.error("无效的知识点ID列表格式，应为逗号分隔的整数")
        sys.exit(1)
    
    # 创建测试工具并运行测试
    tester = APITester(args.url, args.token)
    results = tester.run_all_tests(knowledge_point_ids)
    
    # 检查测试结果
    success_count = sum(1 for result in results.values() if result.get("success", False))
    total_tests = len(results)
    
    if success_count == total_tests:
        logger.info("所有测试都通过了！")
        sys.exit(0)
    else:
        logger.error(f"测试完成，但有 {total_tests - success_count} 个测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 