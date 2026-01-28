import spacy
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)

MAX_TOKENS = 300
MAX_SENT_TOKENS = 200
OVERLAP = 2

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(
            "en_core_web_sm",
            disable=["ner", "tagger"]
        )
    return _nlp

def count_tokens(text):
    return len(
        tokenizer.encode(
            text,
            add_special_tokens=False,
            truncation=True,
            max_length=MAX_SENT_TOKENS
        )
    )

def chunk_text_semantic(text):
    doc = get_nlp()(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = count_tokens(sent)

        if current_tokens + sent_tokens > MAX_TOKENS:
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            current_chunk = current_chunk[-OVERLAP:]
            current_tokens = sum(count_tokens(s) for s in current_chunk)

        current_chunk.append(sent)
        current_tokens += sent_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
