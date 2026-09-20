"""Text -> vector. Two embedders behind one interface, chosen by EMBED_PROVIDER.

hash       a lexical bag-of-words embedding. No model, no download, deterministic. Good enough for
           CI and for seeing the mechanics; it knows nothing about meaning.
fastembed  BAAI/bge-small-en-v1.5 on CPU via fastembed (about 130 MB, downloaded once). Real
           semantic similarity; what the fellow measures against in Week 2.
"""

import hashlib
import re
from typing import Any, Protocol

import numpy as np

from app.settings import get_settings

_TOKEN = re.compile(r"[a-z0-9]+")


class Embedder(Protocol):
    name: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    name = "hash"
    dim = 512

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            v = np.zeros(self.dim, dtype=np.float32)
            for tok in _TOKEN.findall(text.lower()):
                if len(tok) < 3:
                    continue
                h = int(hashlib.blake2b(tok.encode(), digest_size=4).hexdigest(), 16)
                v[h % self.dim] += 1.0
            norm = float(np.linalg.norm(v))
            out.append((v / norm).tolist() if norm else v.tolist())
        return out


class FastEmbedder:
    name = "fastembed"
    dim = 384

    def __init__(self, model: str = "BAAI/bge-small-en-v1.5") -> None:
        self._model_name = model
        self._model: Any = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self._model_name)
        return [list(map(float, vec)) for vec in self._model.embed(texts)]


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        provider = get_settings().embed_provider
        if provider == "hash":
            _embedder = HashEmbedder()
        elif provider == "fastembed":
            _embedder = FastEmbedder()
        else:
            raise ValueError(f"unknown EMBED_PROVIDER {provider!r}; known: hash, fastembed")
    return _embedder


def reset_embedder() -> None:
    global _embedder
    _embedder = None
