import sys
import os
sys.path.append(r'D:\Storage\rag_project\src')

# os.environ["GOOGLE_API_KEY"] = "AIzaSyABvC8mPrwa0Kgy08mFFzkyeh2_N-Bb3lY"  # Thay key thật

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from test_single_file_loader import test_single_file


def test_rag_single(filename):
    print(f"\n FULL RAG TEST: {filename}")
    docs = test_single_file(filename)
    
    # Build FAISS
    print(" Building FAISS...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # LLM + Prompt
    print(" Init Gemini...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key="AIzaSyBKUfFRLphY4AgTY-j5sr-6s0SFWW0ATyg"  # API KEY Ở ĐÂY
    )    

    custom_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""Bạn là bác sĩ nhi khoa. Dựa vào TÀI LIỆU Y KHOA sau:

CONTEXT: {context}

CÂU HỎI: {question}

TRẢ LỜI chính xác dựa trên CONTEXT, ngắn gọn, chuyên nghiệp."""
    )
    
    qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": custom_prompt},
    return_source_documents=True
)
    
    #  CHỈ NHIKHOA2.json - 1 query đúng
    query = "điều trị suy hô hấp"
    
    print(f"\n Query: {query}")
    result = qa_chain.invoke({"query": query})
    print(f" Answer: {result['result'][:400]}...")
    #  FIX: Kiểm tra key tồn tại
    if 'source_documents' in result:
        print(f" Sources: {len(result['source_documents'])} docs")
    else:
        print(" Sources: Không có source_documents (Gemini 2.5 format)")
    
    print("\n RAG SINGLE FILE OK!")

if __name__ == "__main__":
    test_rag_single("NHIKHOA2.json")