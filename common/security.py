import re

_danger_patterns = [
    re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"on\w+\s*=\s*['\"]?[^'\"]+['\"]?", re.IGNORECASE),
    re.compile(r"javascript:\s*", re.IGNORECASE),
    re.compile(r"<\s*/?\s*iframe.*?>", re.IGNORECASE),
]

def sanitize_string(value: str, max_len=800) -> str:
    if not isinstance(value, str):
        return value
    cleaned = value
    for p in _danger_patterns:
        cleaned = p.sub(" ", cleaned)
    cleaned = cleaned.replace('<', '').replace('>', '')
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned.strip()