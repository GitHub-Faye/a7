#!/usr/bin/env python
# coding: utf-8
"""
API测试脚本
用于测试中间件功能，包括JWT认证、请求日志和请求处理
"""

import requests
import json
import time
from pprint import pprint

# 服务器基础URL
BASE_URL = "http://127.0.0.1:8000"

def print_response(resp):
    """打印响应内容"""
    print(f"状态码: {resp.status_code}")
    print("响应头:")
    for k, v in resp.headers.items():
        print(f"  {k}: {v}")
    
    try:
        print("\n响应内容:")
        pprint(resp.json())
    except:
        print("\n响应内容: (非JSON格式)")
        print(resp.text[:200] + "..." if len(resp.text) > 200 else resp.text)
    print("-" * 50)

def test_auth_middleware():
    """测试JWT认证中间件"""
    print("\n测试JWT认证中间件")
    
    # 1. 尝试无令牌访问受保护的API
    print("\n1. 无令牌访问:")
    resp = requests.get(f"{BASE_URL}/api/users/profile/")
    print_response(resp)
    
    # 2. 获取令牌 (通常会先注册用户，这里假设我们已有用户)
    print("\n2. 获取令牌:")
    auth_data = {
        "username": "testuser",  # 假设这个用户已存在
        "password": "testpassword"
    }
    resp = requests.post(f"{BASE_URL}/api/token/", data=auth_data)
    print_response(resp)
    
    # 如果令牌获取成功，保存令牌
    token = None
    if resp.status_code == 200:
        token_data = resp.json()
        token = token_data.get("access")
        print(f"获取到令牌: {token[:15]}...")
    else:
        print("无法获取令牌，后续测试将失败")
    
    # 3. 使用有效令牌访问
    if token:
        print("\n3. 有效令牌访问:")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/api/users/profile/", headers=headers)
        print_response(resp)
    
    # 4. 使用无效令牌访问
    print("\n4. 无效令牌访问:")
    headers = {"Authorization": "Bearer invalidtoken12345"}
    resp = requests.get(f"{BASE_URL}/api/users/profile/", headers=headers)
    print_response(resp)

def test_request_processor_middleware():
    """测试请求处理中间件"""
    print("\n测试请求处理中间件")
    
    # 1. 测试API响应格式标准化
    print("\n1. API响应格式:")
    resp = requests.get(f"{BASE_URL}/api/health-check/")
    print_response(resp)
    
    # 2. 测试额外响应头
    print("\n2. 额外响应头:")
    resp = requests.get(f"{BASE_URL}/api/health-check/")
    print("X-API-Version:", resp.headers.get("X-API-Version"))
    print("X-Content-Type-Options:", resp.headers.get("X-Content-Type-Options"))
    
    # 3. 测试大请求限制 (创建一个超过限制的大请求)
    print("\n3. 大请求限制 (可能会被中间件拒绝):")
    large_data = {"data": "x" * (11 * 1024 * 1024)}  # 11MB数据，超过10MB限制
    try:
        resp = requests.post(f"{BASE_URL}/api/users/register/", json=large_data, timeout=5)
        print_response(resp)
    except Exception as e:
        print(f"发送大请求出错: {e}")

def test_request_logging_middleware():
    """测试请求日志中间件"""
    print("\n测试请求日志中间件")
    
    # 发送几个不同类型的请求，检查日志文件是否记录
    requests.get(f"{BASE_URL}/api/health-check/")
    requests.post(f"{BASE_URL}/api/users/register/", json={"username": "test_log"})
    
    print("已发送测试请求。请检查request.log文件查看是否记录了请求信息")
    print("日志文件路径: D:\\A7\\request.log")
    
    # 测试豁免路径
    print("\n测试豁免路径 (不应记录在日志中):")
    requests.get(f"{BASE_URL}/static/test.css")
    requests.get(f"{BASE_URL}/health-check/")
    
    print("已发送豁免路径请求。请检查日志文件确认这些请求未被记录")

def main():
    """主测试函数"""
    print("开始API中间件测试...\n")
    
    # 1. 测试JWT认证中间件
    test_auth_middleware()
    
    # 2. 测试请求处理中间件
    test_request_processor_middleware()
    
    # 3. 测试请求日志中间件
    test_request_logging_middleware()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 