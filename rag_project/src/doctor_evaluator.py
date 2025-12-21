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
Bạn là bác sĩ nhi khoa. Tạo một ca bệnh THỰC TẾ cho bệnh: {disease}

TRIỆU CHỨNG TỪ TÀI LIỆU:
{symptoms}

YÊU CẦU:
1. Chỉ tạo lời thoại của mẹ bệnh nhân (3-4 câu)
2. PHẢI MÔ TẢ các triệu chứng CỤ THỂ của bệnh {disease} từ tài liệu trên
3. Dùng ngôn ngữ đời thường, tự nhiên
4. Format: "Bé [tên] nhà chị [tên mẹ] bữa nay bị [triệu chứng cụ thể]. Chị lo lắm! [thêm chi tiết triệu chứng]."

VÍ DỤ TỐT:
- Bệnh Viêm phổi → "Bé An bị sốt cao 39 độ, ho có đờm, thở nhanh phì phò"
- Bệnh Suy tim → "Bé Minh thở nhanh, mệt lả, bú kém, chân tay lạnh"

CASE BỆNH:
"""
        result = self.evaluator_llm.invoke([prompt])
        return result.content.strip()


    def evaluate_doctor(self, disease: str):
        print(f"\n ĐÁNH GIÁ: {disease}")
        print("=" * 80)
        
        # 1. RAG tìm TRIỆU CHỨNG
        print("Hệ thống đang TRUY TÌM TRIỆU CHỨNG:")
        symptoms, symptom_sources = self.find_symptoms(disease)
        print(f"Xác định triệu chứng: {symptoms[:100]}...")
        
        # 2. GEMINI tạo CASE
        print("Tiến hành tạo case...")
        patient_case = self.generate_case(disease, symptoms)
        print(f"Case hoàn chỉnh:\n{patient_case}")
        
        # 3. NHẬP TRẢ LỜI BS
        doctor_answer = input("\n NHẬP CÂU TRẢ LỜI CỦA BÁC SĨ:\n").strip()
        
        # 4. RAG chi tiết + Đánh giá (giữ nguyên)
        print("\n TRUY TÌM ĐÁP ÁN CHUẨN:")
        standard_data, all_sources = self.get_detailed_standard_knowledge(disease)
        evaluation = self.detailed_evaluation(doctor_answer, standard_data)
        
        return {
            'case': patient_case,
            'standard': standard_data,
            'evaluation': evaluation,
            'sources': all_sources
        }

    def find_symptoms(self, disease: str):
        """RAG tìm triệu chứng bệnh - CẢI THIỆN"""
        # Query chi tiết hơn để tìm đúng bệnh
        queries = [
            f"{disease} lâm sàng",
            f"{disease} triệu chứng",
            f"{disease} dấu hiệu"
        ]
        
        all_symptoms = []
        sources = []
        for q in queries:
            print(f"🔍 Query: {q}")
            answer, src = self.rag.query(q)
            if answer and len(answer.strip()) > 50:  # Chỉ lấy answer có nội dung
                all_symptoms.append(answer)
                sources.extend(src)
        
        # Gom triệu chứng đầy đủ hơn (không cắt quá ngắn)
        if all_symptoms:
            # Lấy 2 answer tốt nhất, mỗi cái 500 ký tự
            symptoms_summary = "\n\n".join([s[:500] for s in all_symptoms[:2]])
        else:
            symptoms_summary = f"Không tìm thấy thông tin triệu chứng cho {disease}"
        
        print(f"📋 Tìm thấy triệu chứng: {symptoms_summary[:200]}...")
        return symptoms_summary, sources

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
            print(f" {section}:")
            section_content = []
            for q in qlist:
                print(f" {q}")
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
            "diem_so": "85/100",
            "nhan_xet_tong_quan": "..."
            }}

            JSON PURE:
            """
        
        result = self.evaluator_llm.invoke([prompt])
        return result.content