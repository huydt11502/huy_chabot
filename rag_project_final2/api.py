"""
FastAPI Backend for RAG Medical System
Provides REST API for the React frontend to interact with RAG model
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
import sys
import os

# Add src to path - use relative path from this file's location
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir / "src"))

from data_loader import DataLoader
from vector_store import VectorStoreManager
from rag_chain import RAGChain
from doctor_evaluator import DoctorEvaluator
from config import Config

app = FastAPI(
    title="Mocha Medical RAG API",
    description="RAG-powered medical training backend for pediatric cases",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
rag_chain: Optional[RAGChain] = None
evaluator: Optional[DoctorEvaluator] = None
diseases_catalog: List[Dict] = []


# ==================== PYDANTIC MODELS ====================

class DiseaseInfo(BaseModel):
    id: str
    name: str
    source: str
    category: str
    sections: List[str]

class QueryRequest(BaseModel):
    question: str
    k: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]

class CaseGenerateRequest(BaseModel):
    disease: str

class CaseGenerateResponse(BaseModel):
    case: str
    symptoms: str
    disease: str

class EvaluateRequest(BaseModel):
    disease: str
    case: str
    doctor_answer: str

class EvaluateResponse(BaseModel):
    case: str
    standard: str
    evaluation: str
    sources: List[Dict]


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup():
    global rag_chain, evaluator, diseases_catalog
    
    print("🚀 Starting RAG Medical API...")
    print(f"📂 Base dir: {Config.BASE_DIR}")
    
    # Load diseases catalog from JSON files
    diseases_catalog = load_diseases_catalog()
    print(f"📚 Loaded {len(diseases_catalog)} diseases")
    
    # Build vector store and RAG chain
    print("🔨 Building vector store (this may take a minute)...")
    docs = DataLoader.load_all_chunks()
    
    vs_manager = VectorStoreManager()
    vs_manager.build_from_docs(docs)
    
    rag_chain = RAGChain(vs_manager)
    evaluator = DoctorEvaluator(rag_chain)
    
    print("✅ RAG API Ready!")


def load_diseases_catalog() -> List[Dict]:
    """Load all diseases from JSON files"""
    DATA_DIR = Path(Config.BASE_DIR) / "data"
    files = ["BoYTe200_v3.json", "NHIKHOA2.json", "PHACDODIEUTRI_2016.json"]
    
    all_diseases = []
    for filename in files:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            print(f"⚠️ File not found: {filepath}")
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            chapters = json.load(f)
        
        # Categorize by source file
        if "BoYTe200" in filename:
            category = "Quy trình kỹ thuật"
        elif "NHIKHOA" in filename:
            category = "Lý thuyết nhi khoa"
        else:
            category = "Phác đồ điều trị"
        
        for chap in chapters:
            all_diseases.append({
                "id": f"{filename.split('.')[0]}_{chap.get('id')}",
                "name": chap.get("Index", "Unknown"),
                "source": filename,
                "category": category,
                "sections": [c.get("title", "") for c in chap.get("contents", [])]
            })
    
    return all_diseases


def categorize_disease(name: str, sections: List[str]) -> str:
    """Auto-categorize disease based on name and sections"""
    name_lower = name.lower()
    
    if any(kw in name_lower for kw in ["viêm phổi", "ho", "hen", "suyễn", "thở"]):
        return "Hô hấp"
    elif any(kw in name_lower for kw in ["tiêu chảy", "nôn", "ruột", "gan", "dạ dày"]):
        return "Tiêu hóa"
    elif any(kw in name_lower for kw in ["tim", "mạch", "huyết áp"]):
        return "Tim mạch"
    elif any(kw in name_lower for kw in ["não", "co giật", "động kinh"]):
        return "Thần kinh"
    elif any(kw in name_lower for kw in ["sốt", "nhiễm khuẩn", "nhiễm trùng"]):
        return "Nhiễm trùng"
    elif any(kw in name_lower for kw in ["dị ứng", "phát ban"]):
        return "Dị ứng"
    elif any(kw in name_lower for kw in ["kỹ thuật", "quy trình", "nội soi"]):
        return "Kỹ thuật"
    else:
        return "Khác"


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Mocha Medical RAG API",
        "total_diseases": len(diseases_catalog)
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_ready": rag_chain is not None,
        "evaluator_ready": evaluator is not None,
        "diseases_loaded": len(diseases_catalog)
    }


@app.get("/diseases", response_model=List[Dict])
async def get_diseases(category: Optional[str] = None, search: Optional[str] = None):
    """Get all diseases, optionally filtered"""
    result = diseases_catalog.copy()
    
    if category:
        result = [d for d in result if d["category"] == category]
    
    if search:
        search_lower = search.lower()
        result = [d for d in result if search_lower in d["name"].lower()]
    
    return result


@app.get("/diseases/{disease_id}")
async def get_disease(disease_id: str):
    """Get single disease by ID"""
    for d in diseases_catalog:
        if d["id"] == disease_id:
            return d
    raise HTTPException(status_code=404, detail="Disease not found")


@app.get("/categories")
async def get_categories():
    """Get unique categories"""
    categories = set(d["category"] for d in diseases_catalog)
    return [{"name": c, "count": sum(1 for d in diseases_catalog if d["category"] == c)} 
            for c in sorted(categories)]


@app.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """Query the RAG knowledge base"""
    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAG not initialized")
    
    answer, sources = rag_chain.query(request.question)
    
    return {
        "answer": answer,
        "sources": [
            {
                "content": doc.page_content[:500],
                "chunk_title": doc.metadata.get("chunk_title", ""),
                "section_title": doc.metadata.get("section_title", ""),
                "source_file": doc.metadata.get("source_file", "")
            }
            for doc in sources
        ]
    }


@app.post("/generate-case", response_model=CaseGenerateResponse)
async def generate_case(request: CaseGenerateRequest):
    """Generate a patient case for a disease using RAG + LLM"""
    if not evaluator:
        raise HTTPException(status_code=503, detail="Evaluator not initialized")
    
    # Find symptoms via RAG
    symptoms, _ = evaluator.find_symptoms(request.disease)
    
    # Generate case via LLM
    case = evaluator.generate_case(request.disease, symptoms)
    
    return {
        "case": case,
        "symptoms": symptoms,
        "disease": request.disease
    }


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_answer(request: EvaluateRequest):
    """Evaluate doctor's answer against RAG knowledge"""
    if not evaluator:
        raise HTTPException(status_code=503, detail="Evaluator not initialized")
    
    # Get standard knowledge
    standard_data, sources = evaluator.get_detailed_standard_knowledge(request.disease)
    
    # Evaluate doctor's answer
    evaluation = evaluator.detailed_evaluation(request.doctor_answer, standard_data)
    
    return {
        "case": request.case,
        "standard": standard_data,
        "evaluation": evaluation,
        "sources": [
            {
                "content": doc.page_content[:300],
                "chunk_title": doc.metadata.get("chunk_title", ""),
                "section_title": doc.metadata.get("section_title", ""),
                "source_file": doc.metadata.get("source_file", "")
            }
            for doc in sources[:5]
        ]
    }


@app.get("/sections")
async def get_unique_sections():
    """Get all unique section types"""
    sections = set()
    for d in diseases_catalog:
        for s in d["sections"]:
            if s:
                sections.add(s)
    return sorted(sections)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
