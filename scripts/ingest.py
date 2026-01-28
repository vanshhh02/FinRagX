import os
from app.ingest.loaders import load_document
from app.ingest.chunker import chunk_text_semantic
from app.ingest.embedder import get_embedding
from app.ingest.vector_store import LocalVectorStore

vs = LocalVectorStore(dim=1024)

def ingest_folder(folder):
    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        print(f"Ingesting: {file}")

        text, metadata = load_document(path)
        chunks = chunk_text_semantic(text)

        for i, chunk in enumerate(chunks):
            emb = get_embedding(chunk)
            meta = {
                **metadata,
                "chunk_id": i,
                "chunk_text": chunk
            }
            vs.upsert(emb, meta)

    print("Ingestion complete.")
    vs.save()        # 🔥 THIS LINE MAKES IT ENTERPRISE-GRADE


if __name__ == "__main__":
    ingest_folder("./data/")
