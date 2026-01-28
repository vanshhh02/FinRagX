def answer_prompt(context: str, query: str) -> str:
    return f"""
You are an enterprise compliance assistant.

Rules:
- Answer ONLY from the provided context.
- Do NOT use outside knowledge.
- If context is insufficient, say "Insufficient information in documents."
- Be precise and factual.
- Cite articles or sections when possible.

Context:
{context}

Question:
{query}

Answer:
"""
