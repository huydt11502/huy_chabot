import json
from pathlib import Path

"""
 BoYTe200_v3.json: 157 chunks  
 NHIKHOA2.json: 47 chunks     
 PHACDODIEUTRI_2016.json: 156 chunks
 TỔNG: 360 chunks logic 


chunk = {
  "chunk_id": chap["id"],
  "title": chap["Index"], 
  "level1_items": chap["level1_items"],
  "contents": [  # Mảng sections
    {"title": "Section 1", "content": "..."},
    {"title": "Section 2", "content": "..."},
    ...
  ]
}

"""

BASE_DIR = Path(r"D:\Storage\rag_project")  # sửa cho đúng đường dẫn 
DATA_DIR = BASE_DIR / "data"

def load_chapters(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)
    return chapters

def main():
    print(" BASE_DIR:", BASE_DIR)
    print(" DATA_DIR:", DATA_DIR, "\n")

    json_files = list(DATA_DIR.glob("*.json"))
    if not json_files:
        print(" Không tìm thấy file .json nào trong data/")
        return

    total_chunks = 0

    for json_file in json_files:
        print(f"==============================")
        print(f" FILE: {json_file.name}")
        chapters = load_chapters(json_file)

        all_chunks = []
        for chap in chapters:
            all_chunks.append({
                "chunk_id": chap.get("id"),
                "title": chap.get("Index"),
                "level1_items": chap.get("level1_items", []),
                "contents": chap.get("contents", []),
            })

        num_chunks = len(all_chunks)
        total_chunks += num_chunks
        print(f" Số chunk (theo id) trong file này: {num_chunks}")

        # In MẪU 1 chunk đầu tiên của file
        if num_chunks > 0:
            sample = all_chunks[0]
            print("\n MẪU CHUNK ĐẦU TIÊN:")
            print("  chunk_id:", sample["chunk_id"])
            print("  title   :", sample["title"])
            print("  level1_items:", sample["level1_items"])
            print("  Số sections trong contents:", len(sample["contents"]))
            if sample["contents"]:
                sec0 = sample["contents"][0]
                print("  ➜ Section 1 title :", sec0.get("title"))
                print("  ➜ Section 1 content preview:",
                      (sec0.get("content") or "")[:150], "...")
        print()

    print("====================================")
    print(" TỔNG SỐ CHUNK (theo id) TỪ TẤT CẢ FILE:", total_chunks)

if __name__ == "__main__":
    main()
