import re

def smart_trim(text: str, max_len: int = 2000) -> str:
    """
    Trim text intelligently to a maximum length without cutting words in half.
    """
    if len(text) <= max_len:
        return text
    trimmed = text[:max_len].rsplit(" ", 1)[0]  # cut at last full word

def normalize_text(text: str) -> str:
    # lowercase, strip extra spaces, remove non-printable chars
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text
