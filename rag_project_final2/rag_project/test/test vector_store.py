
from src.data_loader import DataLoader
from src.embeddings import EmbeddingsManager


docs = DataLoader.load_all_chunks()

em = EmbeddingsManager()
embeddings_model = em.get_embeddings()

save_documents(docs)
save_embeddings(docs, embeddings_model)
