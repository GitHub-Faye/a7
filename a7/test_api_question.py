import requests
import json

# API端点
url = "http://localhost:8000/api/questions-generate/"

# 请求数据
data = {
    "knowledge_point_ids": [1, 2],
    "question_types": ["short_answer", "multiple_choice"],
    "quantity": 2,
    "difficulty": 3
}

# 发送POST请求
response = requests.post(url, json=data)

# 打印响应状态码和内容
print(f"状态码: {response.status_code}")
print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}") 