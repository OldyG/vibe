from __future__ import annotations

from typing import Optional


def find_javadoc(lines: list[str], anchor_line: int) -> tuple[bool, Optional[int], Optional[int]]:
    if anchor_line <= 1:
        return False, None, None
    idx = anchor_line - 2

    while idx >= 0 and lines[idx].strip() == "":
        idx -= 1
    if idx < 0:
        return False, None, None

    line = lines[idx]
    if "*/" not in line:
        return False, None, None

    end_line = idx + 1
    start_line: Optional[int] = None
    j = idx
    while j >= 0:
        if "/**" in lines[j]:
            start_line = j + 1
            break
        if "/*" in lines[j] and "/**" not in lines[j]:
            return False, None, None
        j -= 1

    if start_line is None:
        return False, None, None

    return True, start_line, end_line


def build_javadoc_dict(
    lines: list[str],
    anchor_line: int,
    max_preview_chars: int,
) -> dict:
    present, start_line, end_line = find_javadoc(lines, anchor_line)
    if not present:
        return {
            "present": False,
            "startLine": None,
            "endLine": None,
            "lineCount": 0,
            "preview": None,
        }

    assert start_line is not None
    assert end_line is not None
    line_count = end_line - start_line + 1
    preview = None
    if max_preview_chars and max_preview_chars > 0:
        raw = "\n".join(lines[start_line - 1 : end_line])
        preview = raw[:max_preview_chars]
    return {
        "present": True,
        "startLine": start_line,
        "endLine": end_line,
        "lineCount": line_count,
        "preview": preview,
    }
