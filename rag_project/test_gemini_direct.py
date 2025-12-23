"""Test Gemini API trực tiếp"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key: {api_key[:20]}..." if api_key else "No API Key found!")

try:
    print("\n🧪 Testing gemini-2.5-flash...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.1
    )
    
    result = llm.invoke("Xin chào, bạn là ai?")
    print(f"✅ SUCCESS: {result.content[:100]}...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
