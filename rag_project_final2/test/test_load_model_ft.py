# test_load_model_fixed.py
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

texts = ["Sốt ở trẻ em", "Trẻ bị sốt cao", "Gãy xương tay"]

print("=== sup-SimCSE-VietNamese-phobert-base ===")
simcse_model = SentenceTransformer("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")
simcse_embeds = simcse_model.encode(texts)
print("v1 ↔ v2:", cosine_similarity([simcse_embeds[0]], [simcse_embeds[1]])[0][0])
print("v1 ↔ v3:", cosine_similarity([simcse_embeds[0]], [simcse_embeds[2]])[0][0])

print("\n=== PhoBERT gốc ===")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
phobert_model = AutoModel.from_pretrained("vinai/phobert-base")

def phobert_embed(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    with torch.no_grad():
        outputs = phobert_model(**inputs)
    attention_mask = inputs['attention_mask']
    embeddings = outputs.last_hidden_state
    mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    return torch.sum(embeddings * mask, 1) / torch.clamp(mask.sum(1), min=1e-9)

phobert_embeds = [phobert_embed(t).squeeze().numpy() for t in texts]
print("v1 ↔ v2:", cosine_similarity([phobert_embeds[0]], [phobert_embeds[1]])[0][0])
print("v1 ↔ v3:", cosine_similarity([phobert_embeds[0]], [phobert_embeds[2]])[0][0])
