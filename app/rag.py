from app.ingest.embedder import get_embedding
from app.ingest.vector_store import LocalVectorStore
from app.hierarchical_retriever import HierarchicalRetriever
from app.agents.orchestrator import Orchestrator
from app.llm import llm


class RAGPipeline:
    """
    Enterprise Hybrid RAG Pipeline
    """

    def __init__(self, top_k=5):
        self.retriever = HierarchicalRetriever()
        self.orch = Orchestrator(llm)
        self.top_k = top_k

    # ------------------------------
    # Main RAG API
    # ------------------------------

    def run(self, query: str):
        # 1. Retrieve grounded chunks
        retrieved_chunks = self.retriever.retrieve(query)

        if len(retrieved_chunks) == 0:
            return {
                "rejected": True,
                "reason": "No relevant documents found.",
                "answer": None,
                "confidence": 0.0,
                "sources": [],
                "citations": []
            }

        # 2. Run Orchestrator (answer + critic loop)
        result = self.orch.run(
            retrieved_chunks,
            query,
            max_iters=2
        )

        # If rejected by critic
        if isinstance(result, dict) and result.get("rejected"):
            return result

        # 3. Build final structured response
        answer = result

        sources = list({c["document"] for c in retrieved_chunks})

        citations = []
        for c in retrieved_chunks[:5]:
            citations.append({
                "doc": c["document"],
                "score": round(float(c["score"]), 4)
            })

        # Simple confidence heuristic
        avg_score = sum(c["score"] for c in retrieved_chunks) / len(retrieved_chunks)
        confidence = round(min(0.95, avg_score), 3)

        return {
            "rejected": False,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "citations": citations
        }
