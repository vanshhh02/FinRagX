import json


class Orchestrator:
    def __init__(self, llm):
        self.llm = llm

    # ------------------------------
    # Build context from chunks
    # ------------------------------

    def _build_context(self, chunks):
        context_blocks = []

        for c in chunks:
            block = (
                f"[DOCUMENT: {c['document']} | SCORE: {round(c['score'], 4)}]\n"
                f"{c['text']}"
            )
            context_blocks.append(block)

        return "\n\n".join(context_blocks)

    # ------------------------------
    # Main reasoning loop
    # ------------------------------

    def run(self, retrieved_chunks, query: str, max_iters: int = 2):
        from app.agents.answer_agent import answer_prompt
        from app.agents.critic_agent import critic_prompt

        context = self._build_context(retrieved_chunks)

        for _ in range(max_iters):
            # 1. Generate answer
            answer = self.llm(answer_prompt(context, query))

            # 2. Critic review
            critique_raw = self.llm(critic_prompt(context, answer))

            try:
                critique = json.loads(critique_raw)
            except Exception:
                return {
                    "rejected": True,
                    "reason": "Critic produced invalid JSON.",
                }

            if critique.get("verdict") == "valid":
                return answer

        # Rejected after iterations
        return {
            "rejected": True,
            "reason": "Answer rejected due to insufficient grounding."
        }
