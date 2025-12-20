from data_loader import DataLoader
from config import Config
from doctor_evaluator import DoctorEvaluator
from vector_store import VectorStoreManager
from rag_chain import RAGChain

def main():
    print("LOADING TẤT CẢ CHUNKS...")
    
    # 1. Load TẤT CẢ 3 JSON → Gộp 1 lần
    docs = DataLoader.load_all_chunks()
    
    # 2. Build FAISS chung
    vs_manager = VectorStoreManager()
    vs_manager.build_from_docs(docs)
    # 3. Tạo RAG chain
    rag = RAGChain(vs_manager)
     
    print("\n CHATBOT Y TẾ READY!")
    print(f"API KEY: {Config.GOOGLE_API_KEY}")
    print(f"Embedding: {Config.EMBEDDING_MODEL}")  
    print(" Gõ câu hỏi (quit để thoát)")
    print("-" * 50)
    
    print("\n CHỈNH THỨC: 1=Chatbot | 2=Đánh giá bác sĩ")
    mode = input("Chọn mode (1/2): ").strip()
    
    if mode == "2":
        """
        # evaluator = DoctorEvaluator(rag)
        # print("\n ĐÁNH GIÁ BÁC SĨ")
        # print("Format: Bệnh + Triệu chứng + Trả lời bác sĩ")
        
        # disease = input("Bệnh: ").strip()
        # symptoms = input("Triệu chứng: ").strip()
        # doctor_answer = input("Trả lời bác sĩ: ").strip()
        """
        # standard, evaluation = evaluator.evaluate_doctor(disease, symptoms, doctor_answer)
        
        # print("\n ĐÁP ÁN CHUẨN:")
        # print(standard)
        # print("\n  NHẬN XÉT:")
        # print(evaluation) 

        """
        1. Nhận case: gồm bệnh + triệu chứng 
        2. Nhận câu trả lời của bác sĩ cho case
        2. RAG truy tìm đáp án chuẩn (CHẨN ĐOÁN + ĐIỀU TRỊ) của case đó
        3. So sánh câu trả lời của bác sĩ vs key answer qua gemini theo các tiêu chí (điem manh, diem yeu, da co, thieu, nhan xet tong quan)
        """ 

        """
        CÓ THỂ THAY ĐỔI LUỒNG TRÊN THÀNH: 
        1. Nhận mỗi triệu chứng --> RAG ra được tên bệnh --> RAG tiếp tên bệnh + CHẨN ĐOÁN + ĐIỀU TRỊ (có thể thêm nếu cần thiết)
        """

        """
        NHỮNG THỨ CẦN RAG ĐƯỢC: 
        1. Nhận một câu bất kỳ nằm trong pdf --> RAG đúng mục chứa câu đó 
        VD: Liều:
        +Trẻ ≤ 5 tuổi: 4 mg
        +Trẻ ≥ 5 tuổi và ≤ 13 (15) tuổi: 5 mg
        +Trẻ ≥ 13 (15) tuổi: 10 mg 
        ==> SUYỄN TRẺ EM (VI. PHÒNG NGỪA)
        2. Nhận triêu chứng --> RAG đúng bệnh có triệu chứng đó 
        3. Nhận mục --> RAG đúng mục đó trả về 

        """

        # result = evaluator.evaluate_doctor(disease, symptoms, doctor_answer)

         
        # print("\n ĐÁP ÁN CHUẨN:")
        # print(result['standard'])  


        disease = input("\n🏥 BỆNH: ").strip()
        
        evaluator = DoctorEvaluator(rag)
        result = evaluator.evaluate_doctor(disease)
        
        print("\n📋 CASE BỆNH NHÂN:")
        print(result['case'])
        print("\n📚 ĐÁP ÁN CHUẨN:")
        print(result['standard'])
        print("\n⚖️ PHÂN TÍCH CHI TIẾT:")
        print(result['evaluation'])

         #  TOP 1 + TÀI LIỆU
        print("\n TOP 1 CHẮC CHẮN:")
        if result['sources'] and result['sources'][0]:
            top_doc = result['sources'][0]
            print(f"[{top_doc.metadata['source_file']}]")
            print(f" {top_doc.metadata['chunk_title']}")
            print(f" {top_doc.metadata['section_title']}")
            print(f" {top_doc.page_content.strip()[:300]}")
            print()
        
        print(" TÀI LIỆU THAM KHẢO:")
        if result['sources']:
            for i, doc in enumerate(result['sources'][:3], 1):
                file = doc.metadata.get("source_file", "N/A")
                chunk_id = doc.metadata.get("chunk_id", "N/A")
                chunk_title = doc.metadata.get("chunk_title", "N/A")
                section_id = doc.metadata.get("section_id", "N/A")
                section_title = doc.metadata.get("section_title", "N/A")
                preview = doc.page_content[:80] + "..." 
                print(f" {i}. [{file}] {chunk_id} | {chunk_title} | {section_id} | {section_title}")
                print(f"     {preview}")
            print()

        print("\n NHẬN XÉT:")
        print(result['evaluation'])
    
    else:
        print("\n CHATBOT Y TẾ READY!")
        print(f"API KEY: {Config.GOOGLE_API_KEY}")
        print(f"Embedding: {Config.EMBEDDING_MODEL}")
        print("Gõ câu hỏi (quit để thoát)")
        print("-" * 50)
        
        # 4. CHAT LOOP - CHỈ HỎI → TRẢ LỜI
        while True:
            query = input(" Bạn: ").strip()
            if query.lower() in ['quit', 'exit', 'bye']:
                print(" Tạm biệt!")
                break
            
            if not query:
                continue
                
            print(" Đang trả lời...")
            answer, sources = rag.query(query)  # LẤY CẢ sources
            
            print(f"\n Trả lời: {answer}\n")

            #  TOP 1 CHẮC CHẮN - FULL CONTENT
            if sources and sources[0]:
                top_doc = sources[0]
                print(" TOP 1 CHẮC CHẮN:")
                print(f" [{top_doc.metadata['source_file']}]")
                print(f"  {top_doc.metadata['chunk_title']}")
                print(f"  {top_doc.metadata['section_title']}")
                print(f"  {top_doc.page_content.strip()[:300]}")  # FULL content
                print()
            
            #  IN 3 RETRIEVED DOCS
            if sources:
                print(" TÀI LIỆU THAM KHẢO:")
                for i, doc in enumerate(sources[:3], 1):  # Top 3
                    file = doc.metadata.get("source_file", "N/A")
                    chunk_id = doc.metadata.get("chunk_id", "N/A")
                    chunk_title = doc.metadata.get("chunk_title", "N/A")
                    section_id = doc.metadata.get("section_id", "N/A")
                    section_title = doc.metadata.get("section_title", "N/A")
                    preview = doc.page_content[:80] + "..." 
                    print(f"  {i}. [{file}] {chunk_id} | {chunk_title} | {section_id} | {section_title}")
                    print(f"     {preview}")
                print()

if __name__ == "__main__":
    main()
