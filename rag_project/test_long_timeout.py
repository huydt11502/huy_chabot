import requests
import json

url = "http://localhost:5000/api/start-case"
data = {
    "disease": "SUY TIM",  # Thử với tên chính xác từ database
    "sessionId": "test456"
}

print("Testing API with longer timeout...")
print(f"Disease: {data['disease']}")

try:
    response = requests.post(url, json=data, timeout=120)  # 2 minutes timeout
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n📋 CASE:")
        print(result.get('case', 'N/A')[:200])
        print("\n🔍 SYMPTOMS:")
        print(result.get('symptoms', 'N/A')[:200])
        print(f"\n📚 SOURCES: {len(result.get('sources', []))}")
    else:
        print(f"\n❌ ERROR:")
        print(response.text)
            
except requests.exceptions.Timeout:
    print("\n⏱️ TIMEOUT after 120 seconds!")
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
