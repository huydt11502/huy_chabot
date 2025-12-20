from langchain_community.vectorstores import FAISS
import re

class HybridRetriever:
    def __init__(self, vectorstore):
        self.vs = vectorstore
    
    def keyword_search(self, query, k=5):
        """Exact keyword matching - PRIORITY 1"""
        keywords = re.findall(r'\b\w{3,}\b', query.lower())
        scored_docs = []
        
        for doc_id, doc in self.vs.docstore._dict.items():
            content_lower = doc.page_content.lower()
            title_lower = doc.metadata.get('chunk_title', '').lower()
            
            # Score cao nếu match title + content
            score = sum(2 if kw in title_lower else 1 
                       for kw in keywords if kw in content_lower or kw in title_lower)
            
            if score > 0:
                scored_docs.append((score, doc))
        
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored_docs[:k]]
    
    def hybrid_search(self, query, k=3):
        """KEYWORD FIRST → Semantic backup"""
        # PRIORITY 1: Keyword exact match
        keyword_docs = self.keyword_search(query, k=k*2)
        
        if keyword_docs:
            print(f" KEYWORD HIT: {len(keyword_docs)} docs")
            return keyword_docs[:k]
        
        # PRIORITY 2: Semantic fallback
        print(" Semantic fallback...")
        semantic_docs = self.vs.similarity_search(query, k=k)
        return semantic_docs
