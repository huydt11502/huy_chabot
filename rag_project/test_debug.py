"""Test with detailed error logging"""
import requests
import json

url = "http://localhost:5000/api/start-case"
data = {
    "disease": "SUY TIM",
    "sessionId": "debug_test"
}

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except requests.exceptions.Timeout:
    print("⏱️ Request timeout - server taking too long")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Type: {type(e)}")
