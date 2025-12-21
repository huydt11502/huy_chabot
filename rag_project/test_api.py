"""Test API endpoint để debug lỗi 500"""
import requests
import json

url = "http://localhost:5000/api/start-case"
data = {
    "disease": "VIÊM PHỔI",
    "sessionId": "test_123"
}

print("Testing /api/start-case endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")
print("-" * 80)

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
