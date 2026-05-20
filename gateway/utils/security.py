import hashlib
import secrets


def generate_api_key() -> str:
    return "mrx_sk_" + secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def key_prefix(api_key: str) -> str:
    return api_key[:12]

