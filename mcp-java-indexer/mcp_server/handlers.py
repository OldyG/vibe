from __future__ import annotations

from typing import Optional

from cache.cache_store import default_cache_store
from parser.indexer import find_symbols, index_java_file
from parser.readers import read_javadoc, read_range


_CACHE = default_cache_store()


def _normalize_index_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "includePrivate": opts.get("includePrivate", True),
        "includeFields": opts.get("includeFields", True),
        "includeInnerClasses": opts.get("includeInnerClasses", True),
        "includeConstructors": opts.get("includeConstructors", True),
        "maxJavadocPreviewChars": opts.get("maxJavadocPreviewChars", 0),
        "stableIds": opts.get("stableIds", True),
    }


def _normalize_range_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "includeLineNumbers": opts.get("includeLineNumbers", True),
        "maxChars": opts.get("maxChars", 20000),
    }


def _normalize_javadoc_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "includeLineNumbers": opts.get("includeLineNumbers", True),
        "maxChars": opts.get("maxChars", 8000),
    }


def _normalize_find_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "matchKind": opts.get("matchKind", "any"),
        "maxResults": opts.get("maxResults", 50),
        "caseSensitive": opts.get("caseSensitive", False),
    }


def java_index(filePath: str, options: Optional[dict] = None) -> dict:
    opts = _normalize_index_options(options)
    return index_java_file(filePath, opts, _CACHE)


def java_read_range(
    filePath: str, startLine: int, endLine: int, options: Optional[dict] = None
) -> dict:
    opts = _normalize_range_options(options)
    return read_range(filePath, startLine, endLine, opts)


def java_read_javadoc(filePath: str, symbolId: str, options: Optional[dict] = None) -> dict:
    opts = _normalize_javadoc_options(options)
    return read_javadoc(filePath, symbolId, opts, _CACHE)


def java_find_symbol(rootDir: str, query: str, options: Optional[dict] = None) -> dict:
    opts = _normalize_find_options(options)
    return find_symbols(rootDir, query, opts)
