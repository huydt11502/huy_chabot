from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY = "AIzaSyBhsaHDerIO-IAf7gEPvjs5Mb1hYOjqOMk"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=API_KEY,
    temperature=0
)

print(f"API KEY: {API_KEY} READY")
resp = llm.invoke("helo")
print(resp.content)
