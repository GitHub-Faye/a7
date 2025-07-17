#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
import sys
import mimetypes

# 测试配置
BASE_URL = "http://localhost:8000"  # 服务器地址
LOGIN_URL = f"{BASE_URL}/api/token/"  # 登录API
UPLOAD_URL = f"{BASE_URL}/api/coursewares/upload/"  # 文件上传API
USERNAME = "js"  # 用户名
PASSWORD = "js12345678"  # 密码
FILE_PATH = "1.docx"  # 要上传的文件路径
COURSEWARE_ID = 1  # 课件ID，根据实际情况修改

def login(username, password):
    """登录并获取JWT令牌"""
    print(f"正在登录用户: {username}...")
    
    # 使用表单数据而不是JSON
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(LOGIN_URL, data=data)
    
    print(f"登录请求URL: {LOGIN_URL}")
    print(f"登录请求方法: POST")
    print(f"登录请求数据: {data}")
    
    if response.status_code == 200:
        response_data = response.json()
        print("登录成功!")
        
        # 检查响应结构并提取令牌
        if "data" in response_data and "access" in response_data["data"]:
            # 令牌在data.access中
            access_token = response_data["data"]["access"]
            print(f"成功获取访问令牌: {access_token[:10]}...")
            return access_token
        elif "access" in response_data:
            # 令牌直接在access中
            access_token = response_data["access"]
            print(f"成功获取访问令牌: {access_token[:10]}...")
            return access_token
        else:
            print(f"错误: 响应中没有找到访问令牌! 响应结构: {response_data.keys()}")
            return None
    else:
        print(f"登录失败! 状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

def get_file_info(file_path):
    """获取文件信息"""
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在!")
        return None
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # 获取MIME类型
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        # 默认类型
        if file_ext == '.pdf':
            content_type = 'application/pdf'
        elif file_ext == '.docx':
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_ext == '.doc':
            content_type = 'application/msword'
        else:
            content_type = 'application/octet-stream'
    
    return {
        'name': file_name,
        'size': file_size,
        'size_mb': file_size / (1024 * 1024),
        'extension': file_ext,
        'content_type': content_type
    }

def upload_file(token, courseware_id, file_path, use_alt_param=False):
    """上传文件到指定课件"""
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在!")
        return None
    
    # 获取并打印文件信息
    file_info = get_file_info(file_path)
    if file_info is None:
        print("无法获取文件信息，终止上传")
        return None
        
    print("\n文件信息:")
    print(f"- 文件名: {file_info['name']}")
    print(f"- 文件大小: {file_info['size']} 字节 ({file_info['size_mb']:.2f} MB)")
    print(f"- 文件类型: {file_info['content_type']}")
    print(f"- 文件扩展名: {file_info['extension']}")
    
    print(f"\n正在上传文件: {file_path} 到课件ID: {courseware_id}...")
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    print(f"请求头: {headers}")
    
    # 准备文件和表单数据 - 尝试不同的参数名称
    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, file_info['content_type'])
        }
        
        # 根据参数选择使用哪个字段名
        if use_alt_param:
            # 尝试使用外键字段名
            data = {
                "courseware": str(courseware_id)  # 使用courseware而不是courseware_id
            }
            print("使用备选参数名: courseware")
        else:
            data = {
                "courseware_id": str(courseware_id)  # 使用默认的courseware_id
            }
            print("使用默认参数名: courseware_id")
        
        print(f"表单数据: {data}")
        print(f"文件名: {os.path.basename(file_path)}")
        
        # 发送请求
        print(f"发送请求到: {UPLOAD_URL}")
        response = requests.post(
            UPLOAD_URL,
            headers=headers,
            data=data,
            files=files
        )
    
    # 处理响应
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    try:
        response_json = response.json()
        print(f"响应内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("文件上传成功!")
            return response_json
        else:
            print(f"文件上传失败! 状态码: {response.status_code}")
            
            # 详细解析错误信息
            if "error_code" in response_json:
                print(f"错误代码: {response_json['error_code']}")
            
            if "message" in response_json:
                print(f"错误信息: {response_json['message']}")
            
            # 检查是否有详细的错误信息
            if "errors" in response_json:
                print(f"详细错误: {response_json['errors']}")
            
            # 尝试从不同的错误结构中提取信息
            if "error" in response_json and isinstance(response_json["error"], dict):
                error_dict = response_json["error"]
                if "details" in error_dict:
                    print(f"错误详情: {error_dict['details']}")
                if "message" in error_dict:
                    print(f"错误消息: {error_dict['message']}")
                if "code" in error_dict:
                    print(f"错误代码: {error_dict['code']}")
            
            # 检查字段级别的错误
            if isinstance(response_json.get('errors'), dict):
                for field, errors in response_json['errors'].items():
                    print(f"字段 '{field}' 错误: {errors}")
            
            return None
    except ValueError:
        print(f"响应不是有效的JSON: {response.text}")
        return None

def main():
    """主函数"""
    # 1. 登录获取令牌
    token = login(USERNAME, PASSWORD)
    if not token:
        print("无法继续测试，登录失败")
        sys.exit(1)
    
    # 2. 上传文件 - 首先尝试默认参数名
    print("\n尝试使用默认参数名 'courseware_id'...")
    result = upload_file(token, COURSEWARE_ID, FILE_PATH, use_alt_param=False)
    
    # 如果失败，尝试使用备选参数名
    if not result:
        print("\n默认参数名失败，尝试使用备选参数名 'courseware'...")
        result = upload_file(token, COURSEWARE_ID, FILE_PATH, use_alt_param=True)
    
    if result:
        print("\n上传结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 显示文件URL
        if "data" in result and "file_url" in result["data"]:
            print(f"\n文件访问URL: {BASE_URL}{result['data']['file_url']}")
    
if __name__ == "__main__":
    main() 