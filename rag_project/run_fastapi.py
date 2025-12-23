"""
Simple wrapper to run FastAPI server with correct path
"""
import os
import sys

# Change to correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

# Now import and run the FastAPI app
if __name__ == '__main__':
    import uvicorn
    from api_server_fastapi import app
    
    print("🌟 Starting FastAPI Server...")
    print("📡 Server: http://localhost:5001")
    print("📚 API Docs: http://localhost:5001/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        log_level="info"
    )
