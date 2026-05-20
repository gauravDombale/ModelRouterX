import hashlib
import math
import httpx
from gateway.config import get_settings


class Embedder:
    dimensions = 1536

    def __init__(self) -> None:
        self.settings = get_settings()

    async def embed(self, text: str) -> list[float]:
        if self.settings.openai_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "text-embedding-3-small",
                    "input": text
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["embedding"]
            except Exception:
                # Fall back to local mock embedding if API call fails
                pass

        # Deterministic local embedding keeps tests/offline dev usable
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


