import sys
import os

# ✅ FIX PATH - QUAN TRỌNG!
sys.path.insert(0, r'D:\Storage\rag_project\src')  # Thêm src vào đầu path

from data_loader import DataLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

docs = DataLoader.load_all_chunks()
print(f"✅ Loaded {len(docs)} docs")

embeddings = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
vs = FAISS.from_documents(docs, embeddings)

query = "X-quang phổi 60-83% bình thường 3 tháng"

# OLD: FAISS thuần
old_docs = vs.similarity_search(query, k=3)
print("\n❌ OLD FAISS:")
for doc in old_docs:
    print(f"  {doc.metadata['chunk_title'][:40]} | {doc.metadata['source_file']}")

# NEW: Keyword boost
keywords = ["X-quang", "phổi", "bình thường", "3 tháng"]
boosted = []
for doc_id, doc in vs.docstore._dict.items():
    score = sum(1 for kw in keywords if kw in doc.page_content.lower())
    if score > 0:
        boosted.append(doc)
        print(f"\n✅ KEYWORD BOOST HIT: score={score}")
        print(f"  {doc.metadata['chunk_title']}")
        print(f"  Preview: {doc.page_content[:100]}...")
        break

if not boosted:
    print("\n❌ KHÔNG TÌM THẤY KEYWORD NÀO!")
