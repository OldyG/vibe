from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# java-analyzer를 path에 추가
_java_analyzer_path = Path(__file__).parent.parent / "java-analyzer"
if str(_java_analyzer_path) not in sys.path:
    sys.path.insert(0, str(_java_analyzer_path))

from cache.cache_store import default_cache_store
from parser.indexer import find_symbols, index_java_file
from parser.readers import read_javadoc, read_range
from parser.formatters import format_ultra_compact, format_compact


_CACHE = default_cache_store()


def _normalize_index_options(options: Optional[dict]) -> dict:
    """
    인덱싱 옵션 정규화

    mode 파라미터를 제외한 나머지 옵션들을 정규화합니다.
    mode는 java_index() 함수에서 별도로 처리됩니다.
    """
    opts = options or {}
    return {
        "includePrivate": opts.get("includePrivate", True),
        "includeFields": opts.get("includeFields", True),
        "includeInnerClasses": opts.get("includeInnerClasses", True),
        "includeConstructors": opts.get("includeConstructors", True),
        "maxJavadocPreviewChars": opts.get("maxJavadocPreviewChars", 0),
        "stableIds": opts.get("stableIds", True),
    }


def _normalize_format_options(options: Optional[dict]) -> dict:
    """
    포맷팅 옵션 정규화 (ultra/compact 모드용)
    """
    opts = options or {}
    return {
        "with_fields": opts.get("withFields", True),
        "scope": opts.get("scope", "all"),
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
    """
    Java 파일 인덱싱 (MCP 도구)

    Args:
        filePath: Java 파일 경로
        options: 옵션 딕셔너리
            - mode: "ultra" | "compact" | "full" (기본값: "ultra")
            - withFields: 필드 포함 여부 (기본값: True)
            - scope: "public" | "protected" | "private" | "all" (기본값: "all")
            - includePrivate: private 심볼 포함 (기본값: True)
            - includeFields: 필드 포함 (기본값: True)
            - includeInnerClasses: 내부 클래스 포함 (기본값: True)
            - includeConstructors: 생성자 포함 (기본값: True)
            - maxJavadocPreviewChars: Javadoc 프리뷰 문자 수 (기본값: 0)

    Returns:
        mode에 따른 인덱싱 결과
    """
    opts = options or {}
    mode = opts.get("mode", "ultra")

    # Full 모드 옵션으로 인덱싱
    index_opts = _normalize_index_options(options)
    full_result = index_java_file(filePath, index_opts, _CACHE)

    # 모드에 따라 포맷팅
    if mode == "ultra":
        format_opts = _normalize_format_options(options)
        return format_ultra_compact(full_result, format_opts)
    elif mode == "compact":
        format_opts = _normalize_format_options(options)
        return format_compact(full_result, format_opts)
    else:  # full
        return full_result


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
