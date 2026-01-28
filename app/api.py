from fastapi import FastAPI
from pydantic import BaseModel
from app.rag import RAGPipeline
import uvicorn

# ------------------------------
# App Init
# ------------------------------

app = FastAPI(
    title="FinRAGX API",
    description="Enterprise Hybrid RAG Backend",
    version="1.0"
)

# Load pipeline ONCE (important for performance)
rag = RAGPipeline(top_k=5)


# ------------------------------
# Request / Response Schemas
# ------------------------------

class AskRequest(BaseModel):
    query: str


class AskResponse(BaseModel):
    rejected: bool
    answer: str | None
    confidence: float
    sources: list
    citations: list
    reason: str | None = None


# ------------------------------
# Health Check
# ------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "FinRAGX"}


# ------------------------------
# Main RAG Endpoint
# ------------------------------

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    result = rag.run(req.query)

    # If rejected
    if result.get("rejected"):
        return {
            "rejected": True,
            "answer": None,
            "confidence": 0.0,
            "sources": [],
            "citations": [],
            "reason": result.get("reason", "Rejected")
        }

    # Accepted
    return {
        "rejected": False,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"],
        "citations": result["citations"],
        "reason": None
    }


# ------------------------------
# Run locally
# ------------------------------

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
