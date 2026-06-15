"""
测试 MinerU API 连接
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

api_token = os.getenv("MINERU_API_TOKEN")
print(f"API Token: {api_token[:20]}...")
print(f"Token 长度: {len(api_token)}")

# 测试简单的 API 调用
import requests

url = "https://mineru.net/api/v1/parse"
headers = {
    "Authorization": f"Bearer {api_token}"
}

print(f"\n尝试连接到: {url}")
print(f"使用 Token: {api_token[:30]}...")

# 先测试一个简单的请求
try:
    response = requests.get(url.replace('/parse', '/health'), headers=headers, timeout=10)
    print(f"Health check 状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}")
except Exception as e:
    print(f"Health check 失败: {e}")

print("\n✅ 配置检查完成")
