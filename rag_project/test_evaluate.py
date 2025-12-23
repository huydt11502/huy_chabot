import requests
import json

# First create a case
print("1️⃣ Creating a case...")
case_response = requests.post(
    "http://localhost:5000/api/start-case",
    json={"disease": "SUY TIM", "sessionId": "eval_test_123"},
    timeout=120
)
print(f"Status: {case_response.status_code}")
if case_response.status_code == 200:
    case_data = case_response.json()
    print(f"✅ Case created, sessionId: {case_data['sessionId']}")
    
    # Now test evaluate
    print("\n2️⃣ Testing evaluate endpoint...")
    eval_data = {
        "sessionId": case_data['sessionId'],
        "diagnosis": {
            "clinical": "Bé thở nhanh, mệt lả",
            "paraclinical": "Chưa làm",
            "definitiveDiagnosis": "Suy tim",
            "differentialDiagnosis": "Viêm phổi",
            "treatment": "Điều trị nội khoa",
            "medication": ""
        }
    }
    
    try:
        eval_response = requests.post(
            "http://localhost:5000/api/evaluate",
            json=eval_data,
            timeout=120
        )
        print(f"Status: {eval_response.status_code}")
        
        if eval_response.status_code == 200:
            result = eval_response.json()
            print(f"✅ SUCCESS!")
            print(f"Evaluation: {result.get('evaluation', {}).get('overall_score', 'N/A')}")
        else:
            print(f"❌ ERROR: {eval_response.text}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
else:
    print(f"❌ Failed to create case: {case_response.text}")
