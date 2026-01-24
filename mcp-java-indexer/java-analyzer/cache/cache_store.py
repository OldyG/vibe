from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional


class CacheStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.cache_dir = base_dir / ".mcp-java-index-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_key(self, file_path: str) -> str:
        digest = hashlib.sha1(file_path.encode("utf-8", errors="replace")).hexdigest()
        return digest

    def _cache_path(self, file_path: str, options_key: Optional[str]) -> Path:
        key = self._path_key(file_path)
        if options_key:
            key = f"{key}-{options_key}"
        return self.cache_dir / f"{key}.json"

    def load(self, file_path: str, content_hash: str, options_key: Optional[str] = None) -> Optional[dict]:
        cache_file = self._cache_path(file_path, options_key)
        if not cache_file.exists():
            return None
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        if data.get("hash") != content_hash:
            return None
        return data

    def save(self, file_path: str, data: dict, options_key: Optional[str] = None) -> None:
        cache_file = self._cache_path(file_path, options_key)
        cache_file.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def default_cache_store() -> CacheStore:
    base = Path.cwd()
    env_override = None
    try:
        import os

        env_override = os.environ.get("MCP_JAVA_INDEX_CACHE_ROOT")
    except Exception:
        env_override = None
    if env_override:
        base = Path(env_override)
    return CacheStore(base)
