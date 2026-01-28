from app.ingest.embedder import get_embedding
from app.ingest.vector_store import LocalVectorStore
from app.ingest.pdf_loader import load_pdf_chunks

def ingest_pdf(path: str):
    vs = LocalVectorStore.load()

    chunks = load_pdf_chunks(path)
    for chunk in chunks:
        emb = get_embedding(chunk["text"])
        vs.upsert(emb, chunk)

    vs.save()
