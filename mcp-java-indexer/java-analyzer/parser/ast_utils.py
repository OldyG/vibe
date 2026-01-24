from __future__ import annotations

from typing import Iterable, Optional

from tree_sitter import Node


def node_text(source_bytes: bytes, node: Node) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def first_named_child(node: Node, types: Iterable[str]) -> Optional[Node]:
    for child in node.named_children:
        if child.type in types:
            return child
    return None


def first_named_descendant(node: Node, type_name: str) -> Optional[Node]:
    if node.type == type_name:
        return node
    for child in node.named_children:
        found = first_named_descendant(child, type_name)
        if found is not None:
            return found
    return None


def first_identifier(node: Node) -> Optional[Node]:
    if node.type == "identifier":
        return node
    for child in node.named_children:
        found = first_identifier(child)
        if found is not None:
            return found
    return None


def modifiers_node(node: Node) -> Optional[Node]:
    by_field = node.child_by_field_name("modifiers")
    if by_field is not None:
        return by_field
    for child in node.named_children:
        if child.type == "modifiers":
            return child
    return None


def extract_modifiers(source_bytes: bytes, node: Node) -> list[str]:
    mods_node = modifiers_node(node)
    if mods_node is None:
        return []
    modifiers: list[str] = []
    for child in mods_node.children:
        text = node_text(source_bytes, child).strip()
        if not text:
            continue
        if text.startswith("@"):
            continue
        modifiers.append(text)
    return modifiers


def modifier_anchor_line(node: Node) -> Optional[int]:
    mods_node = modifiers_node(node)
    if mods_node is None:
        return None
    return mods_node.start_point[0] + 1


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def split_top_level_commas(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in text:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            segment = "".join(current).strip()
            if segment:
                parts.append(segment)
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def strip_prefix_keyword(text: str, keyword: str) -> str:
    prefix = keyword + " "
    text = text.strip()
    if text.startswith(prefix):
        return text[len(prefix):].strip()
    if text == keyword:
        return ""
    return text
