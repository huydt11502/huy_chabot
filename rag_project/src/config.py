import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SỬA ĐƯỜNG DẪN LẠI NHA 
    BASE_DIR = r"D:\Storage\rag_project"
    DATA_DIR = f"{BASE_DIR}/data"
    CHUNK_FILES = [
        f"{DATA_DIR}/BoYTe200_v3.json",
        f"{DATA_DIR}/NHIKHOA2.json",
        f"{DATA_DIR}/PHACDODIEUTRI_2016.json"
    ]    
    # EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" # Model embedding 
    # EMBEDDING_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"
    EMBEDDING_MODEL = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
    
    # GOOGLE API KEY - Thay bằng key của bạn từ https://makersuite.google.com/app/apikey
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'YOUR_API_KEY_HERE')
    
    LLM_MODEL = "gemini-2.5-flash" 
    K_RETRIEVE = 3 # Số Document muốn truy
    TEMPERATURE = 0 

"""
AIzaSyABvC8mPrwa0Kgy08mFFzkyeh2_N-Bb3lY
AIzaSyDJqr4nKDrcfmmuKOdDCHkXRvKA48htD6o
"""