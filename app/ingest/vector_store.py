import faiss
import numpy as np
import pickle
import os


class LocalVectorStore:
    def __init__(self, dim=1024):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.metadata = []

    def upsert(self, vector, meta):
        vec_np = np.array([vector]).astype("float32")
        self.index.add(vec_np)
        self.metadata.append(meta)

    def query(self, vector, top_k=5):
        vec_np = np.array([vector]).astype("float32")
        scores, indices = self.index.search(vec_np, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(score),
                "metadata": self.metadata[idx]
            })

        return results

    def search_grouped_by_document(self, vector, top_k=10, max_docs=3, per_doc_k=2):
        vec_np = np.array([vector]).astype("float32")
        scores, indices = self.index.search(vec_np, top_k)

        hits = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx]
            hits.append({
                "score": float(score),
                "doc": meta.get("filename", "unknown"),
                "text": meta.get("chunk_text", "")
            })

        # Group by document
        doc_groups = {}
        for h in hits:
            doc = h["doc"]
            doc_groups.setdefault(doc, []).append(h)

        # Rank documents
        ranked_docs = sorted(
            doc_groups.items(),
            key=lambda x: max(h["score"] for h in x[1]),
            reverse=True
        )

        results = []
        for doc, chunks in ranked_docs[:max_docs]:
            chunks_sorted = sorted(chunks, key=lambda x: x["score"], reverse=True)
            results.append({
                "doc": doc,
                "chunks": chunks_sorted[:per_doc_k]
            })

        return results

    def save(self, path="data"):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "faiss.index"))

        with open(os.path.join(path, "meta.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    @classmethod
    def load(cls, path="data"):
        index = faiss.read_index(os.path.join(path, "faiss.index"))

        with open(os.path.join(path, "meta.pkl"), "rb") as f:
            metadata = pickle.load(f)

        dim = index.d
        vs = cls(dim=dim)
        vs.index = index
        vs.metadata = metadata

        return vs
