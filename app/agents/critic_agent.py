def critic_prompt(context: str, answer: str) -> str:
    return f"""
You are a strict enterprise compliance reviewer.

Your task:
- Check whether the answer is fully grounded in the provided context.
- If any part of the answer is not supported by the context, reject it.

IMPORTANT RULES:
- You MUST output ONLY valid JSON.
- NO explanations.
- NO markdown.
- NO text outside JSON.

Output format (EXACT):

{{
  "verdict": "valid" or "invalid",
  "reason": "short reason"
}}

Context:
{context}

Answer:
{answer}

Now return ONLY the JSON verdict.
"""
