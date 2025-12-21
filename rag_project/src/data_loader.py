import json 
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from config import Config

class DataLoader:
    @staticmethod
    def load_all_chunks() -> List[Document]:
        BASE_DIR = Path(Config.BASE_DIR)
        DATA_DIR = BASE_DIR / 'data'
        all_docs = []
        
        json_files = [Path(f) for f in Config.CHUNK_FILES if Path(f).exists()]
        print("LOADING CHUNKS TỪ TẤT CẢ JSON:")
        
        for json_file in json_files:
            print(f"{json_file.name}...")
            with open(json_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
            
            #  MỖI chap = 1 chunk
            """
            #  Gom lại theo 1 FILE JSON - CÓ 1 SAMPLE - 1 CHUNK 
            # file_chunks chứa all chunks của json đó 
            # Các chunk được tổ chức lại theo DOCUMENT (page_content + metadata)
            # Với page_content là từng content trong contents của section
            """
            file_chunks = []
            for chap in chapters:
                chunk = {
                    "chunk_id": chap.get("id"),
                    "title": chap.get("Index"),
                    "level1_items": chap.get("level1_items", []),
                    "contents": chap.get("contents", [])
                }
                # Mặc dù là content khác nhau nhưng vẫn thuộc cùng chunk_id, chunk_title
                for i, section in enumerate(chunk["contents"]):
                    doc = Document(
                        page_content=section.get("content", ""),
                        metadata={
                            "source_file": json_file.name,
                            "chunk_id": str(chunk["chunk_id"]),
                            "chunk_title": chunk["title"],
                            "section_id": f"{chunk['chunk_id']}.{i+1}",
                            "section_title": section.get("title", "")
                        }
                    )
                    file_chunks.append(doc)
            
            all_docs.extend(file_chunks)
            print(f"{len(file_chunks)} docs từ {len(chapters)} chunks")
        
        print(f"\nTỔNG {len(all_docs)} documents!")
        return all_docs

# TEST: python data_loader.py
if __name__ == "__main__":
    docs = DataLoader.load_all_chunks()
    print("\n SAMPLE DOC:")
    print("Content:", docs[0].page_content)
    print("Metadata:", docs[0].metadata) 

    """
    OUTPUT SAMPLE
Content: Đặt stent khí  phế quản là kỹ thuật đặt một giá đỡ vào khí, phế quản làm rộng và duy trì khẩu kính đường thở để điều trị một số trường hợp hẹp khí, phế quản bẩm sinh hoặc mắc phải. Đặt stent có thể th
Metadata: {'source_file': 'BoYTe200_v3.json', 'chunk_id': '1', 'chunk_title': 'NỘI SOI ĐẶT STENT KHÍ PHẾ QUẢN BẰNG ỐNG CỨNG', 'section_id': '1.1', 'section_title': 'ĐẠI CƯƠNG'}
    """