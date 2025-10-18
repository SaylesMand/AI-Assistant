import hashlib


def hash_content(text: str) -> str:
    """Возвращает MD5-хэш строки, закодированной в utf-8."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()
