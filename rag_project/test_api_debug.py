import requests
import json

url = "http://localhost:5000/api/start-case"
data = {
    "disease": "Suy tim",
    "sessionId": "test123"
}

print("Testing API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(response.text)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("\n❌ ERROR!")
        try:
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
