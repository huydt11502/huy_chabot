from rag_chain import RAGChain
from vector_store import VectorStoreManager
from data_loader import DataLoader
from config import Config
from langchain_google_genai import ChatGoogleGenerativeAI

class DoctorEvaluator:
    def __init__(self, rag):
        self.rag = rag
        self.evaluator_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        print("DoctorEvaluator: Ready (Gemini + RAG)!")
    
    def generate_case(self, disease: str, symptoms: str):
        """DÙNG GEMINI TẠO CASE - NHANH + ỔN ĐỊNH"""
        prompt = f"""
BỆNH: {disease}
TRIỆU CHỨNG: {symptoms}

Tạo 1 case bệnh nhi THỰC TẾ:
"Bé [TÊN] nhà chị [TÊN MẸ] bữa nay bị [TRIỆU CHỨNG]. Chị lo lắm ạ!"

CASE NGẮN GỌN (3-4 câu):
"""
        result = self.evaluator_llm.invoke([prompt])
        return result.content.strip()

    
    def evaluate_doctor(self, disease: str):
        print(f"\n🔬 ĐÁNH GIÁ: {disease}")
        print("=" * 80)
        
        # 1. RAG tìm TRIỆU CHỨNG
        print("🔍 Hệ thống đang TRUY TÌM TRIỆU CHỨNG:")
        symptoms, symptom_sources = self.find_symptoms(disease)
        print(f"✅ Xác định triệu chứng: {symptoms[:100]}...")
        
        # 2. GEMINI tạo CASE
        print("🤖 Tiến hành tạo case...")
        patient_case = self.generate_case(disease, symptoms)
        print(f"📋 Case hoàn chỉnh:\n{patient_case}")
        
        # 3. NHẬP TRẢ LỜI BS
        doctor_answer = input("\n🩺 NHẬP CÂU TRẢ LỜI CỦA BÁC SĨ:\n").strip()
        
        # 4. RAG chi tiết + Đánh giá (giữ nguyên)
        print("\n🔍 TRUY TÌM ĐÁP ÁN CHUẨN:")
        standard_data, all_sources = self.get_detailed_standard_knowledge(disease)
        evaluation = self.detailed_evaluation(doctor_answer, standard_data)
        
        return {
            'case': patient_case,
            'standard': standard_data,
            'evaluation': evaluation,
            'sources': all_sources
        }

    
        
        # # 1. RAG tìm đáp án chuẩn
        # standard_answer, standard_sources = self.get_standard_knowledge(disease, symptoms)
        
        # 2. So sánh + đánh giá
        # evaluation_json = self.compare_answers(doctor_answer, standard_answer, standard_sources)
        
        # return standard_answer, evaluation   

    #     return {
    #     'standard': standard_answer,
    #     'evaluation': evaluation_json,
    #     'sources': standard_sources  # ✅ SOURCES CHO MAIN IN
    # }  

    def find_symptoms(self, disease: str):
        """RAG tìm triệu chứng bệnh"""
        queries = [
            f"{disease} triệu chứng",
            f"{disease} dấu hiệu",
            f"{disease} biểu hiện"
        ]
        
        all_symptoms = []
        sources = []
        for q in queries:
            print(f"  🔍 {q}")
            answer, src = self.rag.query(q)
            all_symptoms.append(answer)
            sources.extend(src)
        
        # Gom triệu chứng chính
        symptoms_summary = "\n".join([s[:200] for s in all_symptoms[:2]])
        return symptoms_summary, sources

    # def get_standard_knowledge(self, disease: str, symptoms: str):
    #     """RAG tìm CHỈ 2 CỤM: CHẨN ĐOÁN + ĐIỀU TRỊ"""
        
    #     # #  CHỈ 2 QUERY CỐT LÕI

    #     diagnosis_query = f"{disease} CHẨN ĐOÁN"
    #     treatment_query = f"{disease} ĐIỀU TRỊ"
        
    #     print(" TÌM CHẨN ĐOÁN:")
    #     print(f"  {diagnosis_query}")
    #     diag_answer, diag_sources = self.rag.query(diagnosis_query)
    
    #     print(" TÌM ĐIỀU TRỊ:")
    #     print(f"  {treatment_query}")
    #     treat_answer, treat_sources = self.rag.query(treatment_query)
    
    #     all_sources = diag_sources + treat_sources
    #     #  GOM 2 PHẦN CHUẨN
    #     standard_context = f"""
    # CÁCH CHẨN ĐOÁN {disease.upper()} + {symptoms.upper()}:
    # {diag_answer}

    # CÁCH ĐIỀU TRỊ {disease.upper()} + {symptoms.upper()}:
    # {treat_answer}
    # """
        
    #     standard_prompt = f"""
    # Tóm tắt theo format:

    # CÁCH CHẨN ĐOÁN:
    # - [NỘI DUNG CHẨN ĐOÁN]

    # CÁCH ĐIỀU TRỊ:
    # - [NỘI DUNG ĐIỀU TRỊ]

    # {standard_context}
    # """
        
    #     standard_result = self.evaluator_llm.invoke([standard_prompt])
    #     return standard_result.content, all_sources 

    # def compare_answers(self, doctor_answer: str, standard_answer: str, sources: list):
    #     """SO SÁNH BÁC SĨ vs KIẾN THỨC CHUẨN"""
    #     comparison_prompt = f"""
    # BẠN LÀ CHUYÊN GIA Y KHOA ĐÁNH GIÁ BÁC SĨ

    # CÂU TRẢ LỜI BÁC SĨ:
    # {doctor_answer}

    # KIẾN THỨC CHUẨN:
    # {standard_answer}

    # PHÂN TÍCH CHI TIẾT (JSON format):
    # {{
    # "diem_manh": ["Điểm mạnh 1", "Điểm mạnh 2"],
    # "diem_yeu": ["Thiếu gì", "Sai gì"],
    # "da_co": ["Kiến thức đã đúng"],
    # "thieu": ["Cần bổ sung"],
    # "diem_so": "9.5/10",
    # "nhan_xet_tong_quan": "Nhận xét tổng quan"
    # }}

    # JSON PURE - KHÔNG THÊM TEXT:
    # """
        
    #     result = self.evaluator_llm.invoke([comparison_prompt])
    #     return result.content

    def get_detailed_standard_knowledge(self, disease: str):
        """RAG CHẨN ĐOÁN CHI TIẾT + ĐIỀU TRỊ"""
        queries = {
            'LAM_SANG': [f"{disease} lâm sàng"],
            'CAN_LAM_SANG': [f"{disease} cận lâm sàng"],
            'CHAN_DOAN_XAC_DINH': [f"{disease} chẩn đoán xác định"],
            'CHAN_DOAN_PHAN_BIET': [f"{disease} chẩn đoán phân biệt"],
            'DIEU_TRI': [f"{disease} điều trị", f"{disease} thuốc"]
        }
        
        results = {}
        all_sources = []
        
        for section, qlist in queries.items():
            print(f"  {section}:")
            section_content = []
            for q in qlist:
                print(f"    🔍 {q}")
                answer, sources = self.rag.query(q)
                section_content.append(answer)
                all_sources.extend(sources)
            results[section] = "\n".join(section_content[:2])
        
        # Format đẹp
        standard_text = f"""
CHẨN ĐOÁN LÂM SÀNG:
{results['LAM_SANG']}

CHẨN ĐOÁN CẬN LÂM SÀNG:
{results['CAN_LAM_SANG']}

CHẨN ĐOÁN XÁC ĐỊNH:
{results['CHAN_DOAN_XAC_DINH']}

CHẨN ĐOÁN PHÂN BIỆT:
{results['CHAN_DOAN_PHAN_BIET']}

CÁCH ĐIỀU TRỊ:
{results['DIEU_TRI']}
"""
        return standard_text, all_sources
    
    def detailed_evaluation(self, doctor_answer: str, standard_data: str):
        """ĐÁNH GIÁ CHI TIẾT + DIỄN GIẢI"""
        prompt = f"""
BẠN LÀ CHUYÊN GIA Y KHOA ĐÁNH GIÁ BÁC SĨ

CÂU TRẢ LỜI BÁC SĨ:
{doctor_answer}

KIẾN THỨC CHUẨN:
{standard_data}

PHÂN TÍCH CHI TIẾT (JSON):
{{
  "diem_manh": ["..."],
  "diem_yeu": ["..."],
  "da_co": ["..."],
  "thieu": ["..."],
  "dien_giai": ["Giải thích vì sao đúng/thiếu..."],
  "diem_so": "8.5/10",
  "nhan_xet_tong_quan": "..."
}}

JSON PURE:
"""
        
        result = self.evaluator_llm.invoke([prompt])
        return result.content