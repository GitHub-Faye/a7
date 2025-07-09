import os
import requests
import json
import base64
from pathlib import Path

# --- 测试配置 ---
BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = "/api/knowledge-points-to-ppt/"
FULL_API_URL = f"{BASE_URL}{API_ENDPOINT}"
OUTPUT_DIR = Path("api_test_output")

# --- 测试用例定义 ---
def get_test_cases():
    """定义所有API测试用例"""
    
    # 假设数据库中存在ID为1, 2, 3的知识点
    base_payload = {
        "knowledge_point_ids": [1, 2, 3],
        "include_children": True,
        "title": "API生成的演示",
        "return_file_content": True  # 请求API直接返回文件内容
    }
    
    return [
        {
            "name": "Default Theme - PPTX",
            "payload": {**base_payload, "format": "pptx", "visual_style": "default"}
        },
        {
            "name": "Teaching Theme - PDF",
            "payload": {**base_payload, "format": "pdf", "visual_style": "teaching"}
        },
        {
            "name": "Minimalist Theme - HTML",
            "payload": {**base_payload, "format": "html", "visual_style": "minimalist"}
        },
        {
            "name": "Default with Green Scheme",
            "payload": {
                **base_payload,
                "format": "pptx",
                "visual_style": "default",
                "color_scheme": "green"
            }
        },
        {
            "name": "Teaching with Purple Scheme",
            "payload": {
                **base_payload,
                "format": "pdf",
                "visual_style": "teaching",
                "color_scheme": "purple"
            }
        },
        {
            "name": "Invalid Request - No IDs",
            "payload": {"format": "pptx"},
            "expected_status": 400
        }
    ]

def run_api_test(test_case):
    """运行单个API测试用例"""
    name = test_case["name"]
    payload = test_case["payload"]
    expected_status = test_case.get("expected_status", 200)
    
    print(f"--- Running API Test: {name} ---")

    try:
        # 打印请求详情，便于调试
        print(f"  发送请求到: {FULL_API_URL}")
        print(f"  请求数据: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(FULL_API_URL, json=payload, timeout=90)
        
        # 打印响应详情，便于调试
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"  [SUCCESS] 状态码符合预期: {response.status_code}")
        else:
            print(f"  [FAILURE] 状态码不匹配: 预期 {expected_status}, 得到 {response.status_code}")
            print(f"  响应内容: {response.text[:200]}...")  # 只打印前200个字符
            return False

        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"  响应数据: {json.dumps(response_data, ensure_ascii=False)[:200]}...")
                
                # 方法1: 检查API是否直接返回了文件内容
                file_content_b64 = response_data.get("data", {}).get("file_content")
                filename = response_data.get("data", {}).get("filename")
                
                if file_content_b64 and filename:
                    # API返回了Base64编码的文件内容
                    try:
                        file_content = base64.b64decode(file_content_b64)
                        output_path = OUTPUT_DIR / filename
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(file_content)
                        print(f"  [SUCCESS] 从API响应中提取文件内容并保存到: {output_path}")
                        return True
                    except Exception as e:
                        print(f"  [ERROR] 解码文件内容时出错: {e}")
                        return False
                
                # 方法2: 如果API只返回了文件URL，尝试下载
                file_url = response_data.get("data", {}).get("file_url")
                filename = response_data.get("data", {}).get("filename")
                
                if not file_url:
                    print("  [FAILURE] API响应中未找到 file_url")
                    return False

                print(f"  API返回的文件URL: {file_url}")
                print(f"  API返回的文件名: {filename}")
                
                # 修正URL路径中的反斜杠问题
                file_url = file_url.replace('\\', '/')
                
                # 尝试多种URL构建方式
                download_attempts = []
                
                # 1. 使用完整的BASE_URL
                download_url = f"{BASE_URL}{file_url}"
                download_attempts.append(("方式1", download_url))
                
                # 2. 如果文件URL已经包含域名，则直接使用
                if file_url.startswith('http'):
                    download_attempts.append(("方式2", file_url))
                else:
                    # 去掉开头的斜杠（如果有）
                    clean_url = file_url[1:] if file_url.startswith('/') else file_url
                    download_attempts.append(("方式2", f"{BASE_URL}/{clean_url}"))
                
                # 3. 尝试直接从/media/路径获取
                download_attempts.append(("方式3", f"{BASE_URL}/media/{Path(file_url).name}"))
                
                # 4. 尝试从/static/路径获取
                download_attempts.append(("方式4", f"{BASE_URL}/static/{Path(file_url).name}"))
                
                # 5. 尝试直接获取文件名
                download_attempts.append(("方式5", f"{BASE_URL}/{Path(file_url).name}"))
                
                # 逐一尝试下载
                for method, url in download_attempts:
                    print(f"  -> 尝试下载文件 ({method}): {url}")
                    file_response = requests.get(url, timeout=60)
                    
                    if file_response.status_code == 200:
                        output_path = OUTPUT_DIR / filename if filename else OUTPUT_DIR / Path(file_url).name
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(file_response.content)
                        print(f"  [SUCCESS] 文件已下载并保存到: {output_path}")
                        return True
                
                print(f"  [FAILURE] 所有下载尝试均失败")
                
                # 创建一个空文件作为占位符，以便测试可以继续
                output_path = OUTPUT_DIR / f"placeholder_{filename if filename else Path(file_url).name}"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(f"# 占位文件 - 实际下载失败\n文件URL: {file_url}\n下载尝试失败")
                print(f"  [INFO] 已创建占位文件: {output_path}")
                return False
                
            except json.JSONDecodeError:
                # 检查是否直接返回了文件内容（非JSON响应）
                content_type = response.headers.get('Content-Type', '')
                content_disp = response.headers.get('Content-Disposition', '')
                
                if ('application/' in content_type or 'image/' in content_type) and response.content:
                    # 尝试从Content-Disposition中获取文件名
                    filename = None
                    if 'filename=' in content_disp:
                        filename = content_disp.split('filename=')[1].strip('"\'')
                    
                    # 如果没有文件名，生成一个
                    if not filename:
                        if 'pdf' in content_type:
                            filename = 'presentation.pdf'
                        elif 'powerpoint' in content_type or 'pptx' in content_type:
                            filename = 'presentation.pptx'
                        elif 'html' in content_type:
                            filename = 'presentation.html'
                        else:
                            filename = 'presentation.bin'
                    
                    # 保存文件
                    output_path = OUTPUT_DIR / filename
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(response.content)
                    print(f"  [SUCCESS] 直接保存API响应内容到: {output_path}")
                    return True
                else:
                    print(f"  [FAILURE] API响应不是JSON格式，也不是有效的文件内容")
                    print(f"  Content-Type: {content_type}")
                    print(f"  Content-Disposition: {content_disp}")
                    return False
        
        return True

    except requests.RequestException as e:
        print(f"  [ERROR] 请求API时出错: {e}")
        return False
    finally:
        print("-" * (len(name) + 22))
        print()

def main():
    """主函数：运行所有API测试"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    test_cases = get_test_cases()
    
    print("=" * 60)
    print("开始 Marp Service API 集成测试")
    print(f"API 端点: {FULL_API_URL}")
    print("=" * 60)
    
    all_passed = True
    for case in test_cases:
        if not run_api_test(case):
            all_passed = False
            
    print("=" * 60)
    if all_passed:
        print("✅ 所有API测试用例均已成功通过！")
    else:
        print("❌ 部分API测试用例失败。")
    print(f"请检查输出目录: {OUTPUT_DIR.resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    main() 