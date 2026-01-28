import requests
import os
import time

# ---------------------------
# CONFIG
# ---------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"

MAX_RETRIES = 2


# ---------------------------
# LOCAL OLLAMA CALL
# ---------------------------

def call_local(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 400,
            "top_p": 0.9
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()

    return r.json()["response"].strip()


# ---------------------------
# GROQ CALL
# ---------------------------

def call_groq(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise enterprise compliance assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 400
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"].strip()


# ---------------------------
# HYBRID LLM (ENTERPRISE PATTERN)
# ---------------------------

def llm(prompt: str) -> str:
    # Try local first
    for _ in range(MAX_RETRIES):
        try:
            return call_local(prompt)
        except Exception as e:
            local_error = e
            time.sleep(1)

    # Fallback to Groq
    print("\n[LLM] Local unavailable → switching to Groq")

    for _ in range(MAX_RETRIES):
        try:
            return call_groq(prompt)
        except Exception as e:
            api_error = e
            time.sleep(1)

    raise RuntimeError(
        f"Both LLM backends failed:\n"
        f"Local error: {local_error}\n"
        f"Groq error: {api_error}"
    )
