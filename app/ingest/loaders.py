import pdfplumber
import docx

def load_document(path):
    text = ""

    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception:
                    continue

    elif path.endswith(".docx"):
        document = docx.Document(path)
        for para in document.paragraphs:
            text += para.text + "\n"

    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    metadata = {
        "filename": path.split("/")[-1],
        "source": "finance_doc",
    }

    return text, metadata
