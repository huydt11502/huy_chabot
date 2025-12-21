"""Test API với bệnh SUY TIM"""
import requests
import json

url = "http://localhost:5000/api/start-case"
data = {
    "disease": "SUY TIM",
    "sessionId": "test_suy_tim_456"
}

print("Testing SUY TIM case generation...")
print(f"URL: {url}")
print(f"Data: {data}")
print("-" * 80)

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"\n✅ Case được tạo:\n{result.get('case', 'N/A')}")
    print(f"\n📋 Triệu chứng tìm được (500 ký tự đầu):\n{result.get('symptoms', 'N/A')[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
