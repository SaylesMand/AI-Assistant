import hashlib

def hash_content(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()