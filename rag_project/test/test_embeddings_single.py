import sys
sys.path.append(r'D:\Storage\rag_project\src')
from langchain_huggingface import HuggingFaceEmbeddings
from test_single_file_loader import test_single_file

def test_embed_single(filename):
    print(f"\n EMBED TEST: {filename}")
    docs = test_single_file(filename)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Embed 1 doc mẫu
    sample_text = docs[0].page_content[:500]
    vector = embeddings.embed_query(sample_text)
    
    print(f" Embedding shape: {len(vector)}")
    print(f" Vector preview: {vector[:5]}...")
    print(f" READY cho FAISS!")

if __name__ == "__main__":
    test_embed_single("NHIKHOA2.json")
    test_embed_single("PHACDODIEUTRI_2016.json")
