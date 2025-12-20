from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config import Config
from hybrid_retriever import HybridRetriever
from vector_store import VectorStoreManager

class RAGChain:
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0  #  0 để deterministic
        )
        
        self.vectorstore = vector_store_manager.vector_store
        self.retriever = HybridRetriever(self.vectorstore)  #  FIX TYPO
        
        #  PROMPT MỚI: TRẢ NỘI DUNG CHUNK + TÓM TẮT
        self.custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
        Bạn là bác sĩ y khoa. Dựa vào TÀI LIỆU sau:

        CONTEXT:
        {context}

        CÂU HỎI: {question}

        TRẢ LỜI:
        1. TRÍCH DẪN ĐÚNG nội dung từ CONTEXT (giữ nguyên văn bản)
        2. Tóm tắt ngắn gọn nếu cần
        3. Luôn ưu tiên thông tin từ chunk chính xác nhất

        NỘI DUNG TÀI LIỆU:
        """
        )
    
    def query(self, question: str):
        """HYBRID RETRIEVAL + FULL CHUNK CONTENT"""
        
        #  BƯỚC 1: HYBRID SEARCH - PRIORITY KEYWORD
        sources = self.retriever.hybrid_search(question, k=4)
        
        #  BƯỚC 2: RE-RANK theo keyword match
        ranked_sources = self.rerank_sources(sources, question)
        
        #  BƯỚC 3: Tạo context FULL CONTENT
        context = self.build_context(ranked_sources)
        
        #  BƯỚC 4: Generate với prompt rõ ràng
        formatted_prompt = self.custom_prompt.format(
            context=context, 
            question=question
        )
        
        result = self.llm.invoke([formatted_prompt])
        return result.content, ranked_sources
    
    def rerank_sources(self, sources, question):
        """RE-RANK: Keyword match > Semantic"""
        keywords = question.lower().split()
        
        def score_doc(doc):
            content = doc.page_content.lower()
            title = doc.metadata.get('chunk_title', '').lower()
            score = sum(1 for kw in keywords if kw in content or kw in title)
            return score
        
        return sorted(sources, key=score_doc, reverse=True)
    
    def build_context(self, sources):
        """FULL CHUNK CONTENT + METADATA"""
        context_parts = []
        for i, doc in enumerate(sources[:3]):
            file = doc.metadata.get('source_file', 'N/A')
            chunk_title = doc.metadata.get('chunk_title', 'N/A')
            section_title = doc.metadata.get('section_title', 'N/A')
            
            context_parts.append(
                f"[{i+1}] {file} | {chunk_title} | {section_title}\n"
                f"NỘI DUNG:\n{doc.page_content}\n{'='*80}"
            )
        return "\n\n".join(context_parts)
