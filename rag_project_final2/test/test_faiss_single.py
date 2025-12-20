import sys
sys.path.append(r'D:\Storage\rag_project\src')
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from test_single_file_loader import test_single_file

def test_faiss_single(filename):
    print(f"\n FAISS TEST: {filename}")
    docs = test_single_file(filename)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    print(f" FAISS index created: {len(docs)} vectors")
    
    # Test retrieve
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    query = "tuần hoàn" if "NHIKHOA" in filename else "đột tử"
    results = retriever.get_relevant_documents(query)
    
    print(f" Query '{query}' → Found {len(results)} docs:")
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.metadata['chunk_title']}")
    print(" FAISS OK!")

if __name__ == "__main__":
    test_faiss_single("NHIKHOA2.json")
    test_faiss_single("PHACDODIEUTRI_2016.json")
