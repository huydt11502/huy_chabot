import json
from pathlib import Path
from langchain_core.documents import Document

BASE_DIR = Path(r"D:\Storage\rag_project")
DATA_DIR = BASE_DIR / "data"

def test_single_file(filename):
    json_path = DATA_DIR / filename
    print(f"\n{'='*60}")
    print(f" TEST FILE: {filename}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    
    print(f" Chapters: {len(chapters)}")
    
    # Tạo chunks ĐÚNG Colab
    all_chunks = [] 
    # Tạo từng chunk dựa vào id mỗi sample 
    for chap in chapters:
        chunk = {
            "chunk_id": chap.get("id"),
            "title": chap.get("Index"),
            "level1_items": chap.get("level1_items", []),
            "contents": chap.get("contents", [])
        }
        all_chunks.append(chunk)
    
    print(f" Chunks: {len(all_chunks)}")
    
    # Tạo Documents
    docs = []
    # Tạo documents từ all_chunk
    
    for chunk in all_chunks:
        for i, section in enumerate(chunk["contents"]):
            doc = Document(
                page_content=section.get("content", ""),
                metadata={
                    "source_file": filename,
                    "chunk_id": chunk["chunk_id"],
                    "chunk_title": chunk["title"],
                    "section_id": f"{chunk['chunk_id']}.{i+1}",
                    "section_title": section.get("title", "")
                }
            )
            docs.append(doc)
    
    print(f" Documents: {len(docs)}")
    print(f" Mẫu doc 0:")
    print(f"  Title: {docs[0].metadata['chunk_title']}")
    print(f"  Section: {docs[0].metadata["section_id"]}")
    print(f"  Content: {docs[0].page_content[:100]}...")
    return docs

if __name__ == "__main__":
    # Test từng file
    test_single_file("NHIKHOA2.json")
    test_single_file("BoYTe200_v3.json")
    test_single_file("PHACDODIEUTRI_2016.json")
