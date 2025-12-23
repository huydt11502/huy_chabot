"""
FastAPI Server để tích hợp RAG vào Chatbot
Endpoints:
- GET /api/health - Health check
- GET /api/diseases - Lấy danh sách bệnh từ JSON
- POST /api/start-case - Nhận bệnh, tạo case với triệu chứng
- POST /api/evaluate - Nhận đáp án user, trả về kết quả so sánh
- Docs: http://localhost:5000/docs (Swagger UI)
"""
import sys
import io

# Fix encoding for Vietnamese characters in Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import sys
import os
import uvicorn

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from config import Config
from doctor_evaluator import DoctorEvaluator
from vector_store import VectorStoreManager
from rag_chain import RAGChain

app = FastAPI(
    title="Medical RAG API",
    description="RAG-based Medical Diagnosis Assistant",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
print("[*] Initializing RAG system...")
vs_manager = VectorStoreManager()
if not vs_manager.vector_store:
    print("[ERROR] FAISS index not found. Run: python build_faiss.py")
    sys.exit(1)

rag = RAGChain(vs_manager)
evaluator = DoctorEvaluator(rag)
print("[OK] RAG system ready!")

# Store active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic models for request/response
class HealthResponse(BaseModel):
    status: str
    message: str
    embedding_model: str


class Disease(BaseModel):
    id: str
    name: str
    category: str
    source: str
    sections: List[str]


class DiseasesResponse(BaseModel):
    success: bool
    diseases: List[Disease]
    total: int


class StartCaseRequest(BaseModel):
    disease: str
    sessionId: str


class StartCaseResponse(BaseModel):
    success: bool
    sessionId: str
    case: str
    symptoms: str
    sources: List[Dict[str, str]]


class DiagnosisData(BaseModel):
    clinical: Optional[str] = ""
    paraclinical: Optional[str] = ""
    definitiveDiagnosis: Optional[str] = ""
    differentialDiagnosis: Optional[str] = ""
    treatment: Optional[str] = ""
    medication: Optional[str] = ""


class EvaluateRequest(BaseModel):
    sessionId: str
    diagnosis: DiagnosisData


class EvaluateResponse(BaseModel):
    success: bool
    case: str
    standardAnswer: Dict[str, Any]
    evaluation: Dict[str, Any]
    sources: List[Dict[str, str]]


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status='healthy',
        message='FastAPI RAG Server is running',
        embedding_model=Config.EMBEDDING_MODEL
    )


@app.get("/api/diseases", response_model=DiseasesResponse)
async def get_diseases(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Lấy danh sách bệnh từ 3 file JSON (Index field)
    Query params:
    - category: Filter by category (procedures, pediatrics, treatment)
    - search: Search in disease names
    """
    try:
        diseases = []
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Mapping files to categories
        files = [
            ('BoYTe200_v3.json', 'procedures'),
            ('NHIKHOA2.json', 'pediatrics'),
            ('PHACDODIEUTRI_2016.json', 'treatment')
        ]
        
        for filename, cat in files:
            # Filter by category if specified
            if category and category != 'all' and category != cat:
                continue
                
            filepath = os.path.join(data_dir, filename)
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    disease_name = item.get('Index', '')
                    
                    # Filter by search if specified
                    if search and search.lower() not in disease_name.lower():
                        continue
                    
                    diseases.append(Disease(
                        id=f"{cat}_{item['id']}",
                        name=disease_name,
                        category=cat,
                        source=filename,
                        sections=item.get('level1_items', [])
                    ))
        
        return DiseasesResponse(
            success=True,
            diseases=diseases,
            total=len(diseases)
        )
    
    except Exception as e:
        print(f"[ERROR] Error in get_diseases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/start-case", response_model=StartCaseResponse)
async def start_case(request: StartCaseRequest):
    """
    Gọi các hàm CÓ SẴN như trong main.py
    1. find_symptoms() - RAG tìm triệu chứng
    2. generate_case() - Gemini tạo case
    3. get_detailed_standard_knowledge() - RAG lấy đáp án chuẩn
    """
    try:
        disease = request.disease.strip()
        session_id = request.sessionId
        
        if not disease:
            raise HTTPException(status_code=400, detail="Disease name is required")
        
        print(f"[INFO] Starting case for disease: {disease}")
        print(f"[INFO] Session ID: {session_id}")
        
        # 1. RAG tìm TRIỆU CHỨNG (như main.py)
        print("[INFO] Step 1: Finding symptoms...")
        symptoms, symptom_sources = evaluator.find_symptoms(disease)
        print(f"[INFO] Found symptoms (first 200 chars): {symptoms[:200]}...")
        
        # 2. GEMINI tạo CASE (như main.py)
        print("[INFO] Step 2: Generating patient case...")
        patient_case = evaluator.generate_case(disease, symptoms)
        print(f"[INFO] Generated case (first 200 chars): {patient_case[:200]}...")
        
        # 3. RAG lấy đáp án chuẩn (như main.py)
        print("[INFO] Step 3: Getting standard knowledge...")
        standard_data, all_sources = evaluator.get_detailed_standard_knowledge(disease)
        print(f"[INFO] Standard data retrieved (length: {len(standard_data)} chars)")
        
        # Lưu vào session để /evaluate dùng
        session_data = {
            'disease': disease,
            'case': patient_case,
            'symptoms': symptoms,
            'standard': standard_data,
            'sources': all_sources
        }
        active_sessions[session_id] = session_data
        
        return StartCaseResponse(
            success=True,
            sessionId=session_id,
            case=patient_case,
            symptoms=symptoms[:300] + "...",
            sources=[
                {
                    'file': doc.metadata.get('source_file', ''),
                    'title': doc.metadata.get('chunk_title', ''),
                    'section': doc.metadata.get('section_title', '')
                }
                for doc in all_sources[:3]
            ]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error in start_case: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate", response_model=EvaluateResponse)
async def evaluate_diagnosis(request: EvaluateRequest):
    """
    Nhận câu trả lời user, so sánh với đáp án chuẩn đã có trong session
    """
    try:
        session_id = request.sessionId
        diagnosis = request.diagnosis
        
        if not session_id or session_id not in active_sessions:
            raise HTTPException(status_code=400, detail="Invalid or expired session")
        
        session_data = active_sessions[session_id]
        disease = session_data['disease']
        patient_case = session_data['case']
        standard_answer = session_data['standard']
        sources = session_data['sources']
        
        print(f"[INFO] Evaluating diagnosis for: {disease}")
        print(f"[INFO] Session ID: {session_id}")
        print(f"[INFO] User diagnosis: {diagnosis.dict()}")
        
        # Format user's answer
        user_answer = f"""
CHẨN ĐOÁN:
- Lâm sàng: {diagnosis.clinical or 'Không có'}
- Cận lâm sàng: {diagnosis.paraclinical or 'Không có'}
- Chẩn đoán xác định: {diagnosis.definitiveDiagnosis or 'Không có'}
- Chẩn đoán phân biệt: {diagnosis.differentialDiagnosis or 'Không có'}

KẾ HOẠCH ĐIỀU TRỊ:
- Cách điều trị: {diagnosis.treatment or 'Không có'}
- Thuốc: {diagnosis.medication or 'Không có'}
"""
        print(f"[INFO] Formatted user answer (first 300 chars): {user_answer[:300]}...")
        
        print("[INFO] Step 1: Evaluating with Gemini...")
        # Gemini đánh giá (dùng hàm CÓ SẴN: detailed_evaluation)
        evaluation_result = evaluator.detailed_evaluation(user_answer, standard_answer)
        print(f"[INFO] Step 2: Evaluation result (first 500 chars): {evaluation_result[:500]}...")
        
        # Parse JSON from evaluation
        print("[INFO] Step 3: Parsing JSON evaluation...")
        try:
            import json
            # Remove markdown code blocks if present
            eval_text = evaluation_result.strip()
            if eval_text.startswith('```'):
                lines = eval_text.split('\n')
                eval_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else eval_text
                if eval_text.startswith('json'):
                    eval_text = eval_text[4:].strip()
            evaluation_obj = json.loads(eval_text)
            print(f"[INFO] Successfully parsed JSON: {json.dumps(evaluation_obj, ensure_ascii=False, indent=2)[:500]}...")
        except Exception as parse_error:
            print(f"[ERROR] Failed to parse JSON: {parse_error}")
            print(f"[ERROR] Raw evaluation text: {evaluation_result[:500]}...")
            # If parsing fails, return as text
            evaluation_obj = {
                'evaluation_text': evaluation_result,
                'diem_so': 'N/A',
                'diem_manh': [],
                'diem_yeu': ['Không thể parse JSON từ đánh giá'],
                'da_co': [],
                'thieu': [],
                'dien_giai': evaluation_result,
                'nhan_xet_tong_quan': 'Lỗi parse JSON'
            }
        
        # Format sources
        formatted_sources = [
            {
                'file': doc.metadata.get('source_file', ''),
                'title': doc.metadata.get('chunk_title', ''),
                'section': doc.metadata.get('section_title', '')
            }
            for doc in sources[:3]
        ]
        
        print("[INFO] Step 4: Formatting response...")
        print(f"[INFO] Evaluation object keys: {list(evaluation_obj.keys())}")
        print(f"[INFO] Standard answer length: {len(standard_answer)} chars")
        print(f"[INFO] Number of sources: {len(formatted_sources)}")
        
        return EvaluateResponse(
            success=True,
            case=patient_case,
            standardAnswer={
                "content": standard_answer,
                "disease": disease
            },
            evaluation=evaluation_obj,
            sources=formatted_sources
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error in evaluate: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    print("[*] Starting FastAPI Server...")
    print(f"[*] Server: http://localhost:8001")
    print(f"[*] Docs: http://localhost:8001/docs")
    print(f"[*] Using API Key: {Config.GOOGLE_API_KEY[:20]}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False  # Set to True for development
    )
