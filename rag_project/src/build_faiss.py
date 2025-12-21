from vector_store import VectorStoreManager
from data_loader import DataLoader

if __name__ == "__main__":
    print(" BUILD FAISS CACHE (2p)")
    all_docs = DataLoader.load_all_chunks()
    vs = VectorStoreManager()
    vs.build_and_cache(all_docs)  # Embed + SAVE
    print(" DONE! Cache ready!")
