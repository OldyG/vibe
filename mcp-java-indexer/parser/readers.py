from __future__ import annotations

from pathlib import Path
from typing import Optional

from cache.cache_store import CacheStore, default_cache_store
from parser.indexer import find_symbol_by_id, index_java_file


def _read_lines(file_path: str) -> list[str]:
    text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    return text.splitlines()


def read_range(file_path: str, start_line: int, end_line: int, options: Optional[dict] = None) -> dict:
    opts = options or {}
    include_numbers = opts.get("includeLineNumbers", True)
    max_chars = int(opts.get("maxChars", 20000))

    lines = _read_lines(file_path)
    line_count = len(lines)

    if start_line < 1 or end_line < start_line or end_line > line_count:
        raise ValueError("Invalid line range")

    output_lines: list[str] = []
    total_chars = 0

    for idx in range(start_line - 1, end_line):
        line_text = lines[idx]
        if include_numbers:
            line_text = f"{idx + 1}: {line_text}"
        projected = total_chars + len(line_text) + 1
        if projected > max_chars:
            output_lines.append("... [truncated]")
            break
        output_lines.append(line_text)
        total_chars = projected

    return {
        "filePath": file_path,
        "startLine": start_line,
        "endLine": end_line,
        "content": "\n".join(output_lines),
    }


def read_javadoc(
    file_path: str,
    symbol_id: str,
    options: Optional[dict] = None,
    cache_store: Optional[CacheStore] = None,
) -> dict:
    opts = options or {}
    cache = cache_store or default_cache_store()
    include_numbers = opts.get("includeLineNumbers", True)
    max_chars = int(opts.get("maxChars", 8000))

    index_data = index_java_file(file_path, options={}, cache_store=cache)
    symbol = find_symbol_by_id(index_data, symbol_id)
    if not symbol:
        return {
            "filePath": file_path,
            "symbolId": symbol_id,
            "found": False,
            "startLine": None,
            "endLine": None,
            "lineCount": 0,
            "content": "",
        }

    javadoc = symbol.get("javadoc") or {}
    if not javadoc.get("present"):
        return {
            "filePath": file_path,
            "symbolId": symbol_id,
            "found": False,
            "startLine": None,
            "endLine": None,
            "lineCount": 0,
            "content": "",
        }

    start_line = javadoc.get("startLine")
    end_line = javadoc.get("endLine")
    if start_line is None or end_line is None:
        return {
            "filePath": file_path,
            "symbolId": symbol_id,
            "found": False,
            "startLine": None,
            "endLine": None,
            "lineCount": 0,
            "content": "",
        }

    content = read_range(
        file_path,
        start_line,
        end_line,
        options={"includeLineNumbers": include_numbers, "maxChars": max_chars},
    )["content"]

    return {
        "filePath": file_path,
        "symbolId": symbol_id,
        "found": True,
        "startLine": start_line,
        "endLine": end_line,
        "lineCount": end_line - start_line + 1,
        "content": content,
    }
