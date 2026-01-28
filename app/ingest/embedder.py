from sentence_transformers import SentenceTransformer

# Switch to a modern, high-quality embedding model
model = SentenceTransformer("intfloat/e5-large-v2")

def get_embedding(text: str):
    # E5 uses a special prompt
    formatted = f"passage: {text}"
    emb = model.encode(formatted, normalize_embeddings=True)
    return emb.tolist()