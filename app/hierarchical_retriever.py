from app.ingest.embedder import get_embedding
from app.ingest.vector_store import LocalVectorStore


class HierarchicalRetriever:
    """
    Enterprise hierarchical retriever:
    Returns structured chunks for orchestration layer
    """

    def __init__(self, top_k_chunks=15, max_docs=3, max_chunks_per_doc=4):
        self.vs = LocalVectorStore.load()
        self.top_k_chunks = top_k_chunks
        self.max_docs = max_docs
        self.max_chunks_per_doc = max_chunks_per_doc

    def retrieve(self, query: str):
        # 1. Embed query
        query_emb = get_embedding(query)

        # 2. Retrieve grouped results
        grouped = self.vs.search_grouped_by_document(
            query_emb,
            top_k=self.top_k_chunks,
            max_docs=self.max_docs,
            per_doc_k=self.max_chunks_per_doc
        )

        # 3. Flatten into structured chunks
        results = []

        for doc_block in grouped:
            doc = doc_block["doc"]
            chunks = doc_block["chunks"]

            for i, c in enumerate(chunks):
                results.append({
                    "document": doc,
                    "chunk_id": i,
                    "score": c["score"],
                    "text": c["text"]
                })

        return results
