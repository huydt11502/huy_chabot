import os
import sys
import json
from pathlib import Path
from langchain_core.documents import Document

#  PATH ĐÚNG
BASE_DIR = Path(r'D:\Storage\rag_project')
sys.path.insert(0, str(BASE_DIR / 'src'))

print(" Đường dẫn Python search:")
print(f"  - BASE_DIR: {BASE_DIR}")

#  LOAD TẤT CẢ JSON TRONG DATA/
DATA_DIR = BASE_DIR / 'data'
all_docs = []

print("\n TẤT CẢ JSON TRONG DATA:")
json_files = list(DATA_DIR.glob("*.json"))
for json_file in json_files:
    print(f"   {json_file.name}")

# Load TẤT CẢ JSON files
total_chunks = 0
for json_file in json_files:
    print(f"\n Đang load {json_file.name}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    
    # Tạo chunks như notebook gốc
    file_chunks = []
    for chap in chapters:
        all_chunks = {
            "chunkid": chap.get("id", "unknown"),
            "title": chap.get("index", "unknown"),
            "level1items": chap.get("level1items", []),
            "contents": chap.get("contents", [])
        }
        
        # Tạo Documents
        for i, section in enumerate(all_chunks["contents"]):
            doc = Document(
                page_content=section["content"],
                metadata={
                    "source_file": json_file.name,
                    "chunkid": all_chunks["chunkid"],
                    "sectionid": f"{all_chunks['chunkid']}.{i+1}",
                    "title": all_chunks["title"],
                    "sectiontitle": section["title"]
                }
            )
            file_chunks.append(doc)
    
    all_docs.extend(file_chunks)
    total_chunks += len(file_chunks)
    print(f"   {json_file.name}: {len(file_chunks)} chunks")

print(f"\n TỔNG KẾT:")
print(f" Tổng chunks từ {len(json_files)} files: {total_chunks}")
print(f" Chunk mẫu 1:")
if all_docs:
    doc = all_docs[0]
    print(f"  File: {doc.metadata['source_file']}")
    print(f"  Content: {doc.page_content[:150]}...")
    print(f"  Title: {doc.metadata['title']}")

print("\n READY CHO RAG - FAISS + LLM!")
