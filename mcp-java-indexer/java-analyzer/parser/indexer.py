from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tree_sitter import Language, Parser
import tree_sitter_java

from cache.cache_store import CacheStore, default_cache_store
from parser.ast_utils import (
    extract_modifiers,
    first_identifier,
    first_named_child,
    first_named_descendant,
    modifier_anchor_line,
    node_text,
    normalize_whitespace,
    split_top_level_commas,
    strip_prefix_keyword,
)
from parser.javadoc import build_javadoc_dict


CLASS_NODE_KINDS = {
    "class_declaration": "class",
    "interface_declaration": "interface",
    "enum_declaration": "enum",
    "record_declaration": "record",
    "annotation_type_declaration": "annotation",
}


@dataclass
class ParseContext:
    source_bytes: bytes
    lines: list[str]
    package_name: str
    options: dict


_JAVA_LANGUAGE = Language(tree_sitter_java.language())
_PARSER = Parser(_JAVA_LANGUAGE)


def _compute_hash(source_bytes: bytes) -> str:
    return hashlib.sha1(source_bytes).hexdigest()


def _options_cache_key(options: dict) -> str:
    serialized = json.dumps(options, sort_keys=True, ensure_ascii=True)
    return hashlib.sha1(serialized.encode("utf-8")).hexdigest()


def _read_file_bytes(file_path: str) -> bytes:
    return Path(file_path).read_bytes()


def _read_file_lines(source_bytes: bytes) -> list[str]:
    text = source_bytes.decode("utf-8", errors="replace")
    return text.splitlines()


def _package_name(root, source_bytes: bytes) -> str:
    pkg_node = first_named_child(root, ["package_declaration"])
    if pkg_node is None:
        return ""
    text = node_text(source_bytes, pkg_node).strip()
    text = strip_prefix_keyword(text, "package")
    text = text.rstrip(";")
    return text.strip()


def _build_qualified_name(package: str, outers: list[str], name: str) -> str:
    parts = []
    if package:
        parts.append(package)
    parts.extend(outers)
    parts.append(name)
    return ".".join(parts)


def _extract_extends(node, source_bytes: bytes, kind: str) -> Optional[str]:
    for child in node.named_children:
        if child.type == "superclass":
            text = node_text(source_bytes, child)
            text = strip_prefix_keyword(text, "extends")
            text = normalize_whitespace(text)
            return text or None
    if kind == "interface":
        for child in node.named_children:
            if child.type == "extends_interfaces":
                text = node_text(source_bytes, child)
                text = strip_prefix_keyword(text, "extends")
                text = normalize_whitespace(text)
                if not text:
                    return None
                parts = split_top_level_commas(text)
                return ", ".join(parts) if parts else None
    return None


def _extract_implements(node, source_bytes: bytes, kind: str) -> list[str]:
    for child in node.named_children:
        if child.type in ("interfaces", "implements_interfaces"):
            text = node_text(source_bytes, child)
            text = strip_prefix_keyword(text, "implements")
            text = normalize_whitespace(text)
            if not text:
                return []
            return split_top_level_commas(text)
        if child.type == "super_interfaces" and kind != "interface":
            text = node_text(source_bytes, child)
            text = strip_prefix_keyword(text, "implements")
            text = normalize_whitespace(text)
            if not text:
                return []
            return split_top_level_commas(text)
    return []


def _extract_annotations_from_signature(signature_text: str) -> list[str]:
    """
    signatureText에서 어노테이션 추출

    더 안정적이고 간단한 방법: 이미 생성된 signature에서 파싱

    Args:
        signature_text: 시그니처 텍스트 (예: "@Service @Transactional public class Foo")

    Returns:
        어노테이션 문자열 리스트 (예: ["@Service", "@Transactional"])
    """
    if not signature_text:
        return []

    annotations = []
    tokens = signature_text.split()

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("@"):
            # 파라미터가 있는 어노테이션 처리: @MyAnno(value="x", flag=true)
            if "(" in token:
                # 같은 토큰 안에 닫는 괄호가 있으면 완성
                if ")" in token:
                    annotations.append(token)
                    i += 1
                else:
                    # 여러 토큰에 걸쳐 있는 경우
                    full_anno = token
                    i += 1
                    while i < len(tokens) and ")" not in tokens[i-1]:
                        full_anno += " " + tokens[i]
                        i += 1
                        if ")" in tokens[i-1]:
                            break
                    annotations.append(full_anno)
            else:
                # 파라미터가 없는 단순 어노테이션
                annotations.append(token)
                i += 1
        elif token in ["public", "private", "protected", "class", "interface", "enum", "record", "@interface", "static", "final", "abstract"]:
            # 어노테이션 영역 종료
            break
        else:
            i += 1

    return annotations


def _extract_annotations(node, source_bytes: bytes) -> list[str]:
    """
    AST에서 어노테이션 노드 추출

    Args:
        node: AST 노드 (클래스, 메서드, 필드 등)
        source_bytes: 소스 코드 바이트

    Returns:
        어노테이션 문자열 리스트 (예: ["@Service", "@Transactional"])
    """
    annotations = []

    # 모든 children과 named_children 탐색
    for child in node.children:
        if child.type == "marker_annotation":
            # @Service, @Deprecated 등 (파라미터 없음)
            name_node = child.child_by_field_name("name")
            if name_node:
                anno_name = "@" + node_text(source_bytes, name_node)
                if anno_name not in annotations:
                    annotations.append(anno_name)
            else:
                # name 필드가 없는 경우 전체 텍스트 사용
                text = node_text(source_bytes, child).strip()
                if text and text not in annotations:
                    annotations.append(text)
        elif child.type == "annotation":
            # @RequestMapping("/api"), @MyAnno(value="x") 등 (파라미터 있음)
            # 전체 어노테이션 텍스트 추출
            full_text = node_text(source_bytes, child).strip()
            # 멀티라인 어노테이션을 한 줄로
            full_text = normalize_whitespace(full_text)
            if full_text and full_text not in annotations:
                annotations.append(full_text)
        elif child.type == "modifiers":
            # modifiers 노드 안에 어노테이션이 있을 수 있음
            for mod_child in child.children:
                if mod_child.type == "marker_annotation":
                    name_node = mod_child.child_by_field_name("name")
                    if name_node:
                        anno_name = "@" + node_text(source_bytes, name_node)
                        if anno_name not in annotations:
                            annotations.append(anno_name)
                    else:
                        text = node_text(source_bytes, mod_child).strip()
                        if text and text not in annotations:
                            annotations.append(text)
                elif mod_child.type == "annotation":
                    full_text = node_text(source_bytes, mod_child).strip()
                    full_text = normalize_whitespace(full_text)
                    if full_text and full_text not in annotations:
                        annotations.append(full_text)

    # AST에서 추출 실패 시, signature에서 추출 시도
    if not annotations:
        # signature_text는 호출자가 생성하므로 여기서는 빈 리스트 반환
        pass

    return annotations


def _type_text(node, source_bytes: bytes) -> str:
    if node is None:
        return ""
    return normalize_whitespace(node_text(source_bytes, node))


def _find_body_node(node):
    body = node.child_by_field_name("body")
    if body is not None:
        return body
    for child in node.named_children:
        if child.type.endswith("_body") or child.type in ("class_body", "interface_body", "enum_body"):
            return child
    return None


def _signature_text(node, source_bytes: bytes) -> str:
    body = None
    for child in node.named_children:
        if child.type in ("block", "constructor_body", "method_body", "class_body", "interface_body"):
            body = child
            break
    if body is not None:
        snippet = source_bytes[node.start_byte : body.start_byte]
    else:
        snippet = source_bytes[node.start_byte : node.end_byte]
    text = snippet.decode("utf-8", errors="replace")
    text = text.rstrip("{;")
    return normalize_whitespace(text)


def _throws_list(node, source_bytes: bytes) -> list[str]:
    for child in node.named_children:
        if child.type == "throws":
            text = node_text(source_bytes, child)
            text = strip_prefix_keyword(text, "throws")
            text = normalize_whitespace(text)
            if not text:
                return []
            return split_top_level_commas(text)
    return []


def _find_formal_parameters(node):
    return first_named_descendant(node, "formal_parameters")


def _param_type_and_name(param_node, source_bytes: bytes) -> Optional[dict]:
    name_node = param_node.child_by_field_name("name")
    if name_node is None:
        name_node = first_identifier(param_node)
    if name_node is None:
        return None
    name = node_text(source_bytes, name_node)
    type_node = param_node.child_by_field_name("type")
    type_text = ""
    if type_node is not None:
        type_text = _type_text(type_node, source_bytes)
    else:
        raw = source_bytes[param_node.start_byte : name_node.start_byte].decode(
            "utf-8", errors="replace"
        )
        type_text = normalize_whitespace(raw)
    return {"name": name, "typeText": type_text}


def _parse_parameters(node, source_bytes: bytes) -> list[dict]:
    params_node = _find_formal_parameters(node)
    if params_node is None:
        return []
    params: list[dict] = []
    for child in params_node.named_children:
        if child.type in ("formal_parameter", "spread_parameter", "receiver_parameter", "inferred_parameter"):
            param = _param_type_and_name(child, source_bytes)
            if param:
                params.append(param)
    return params


def _build_symbol_id(prefix: str, class_name: str, detail: str, start: int, end: int) -> str:
    return f"{prefix}#{class_name}#{detail}|start:{start}|end:{end}"


def _class_symbol_id(kind: str, qualified_name: str, start: int, end: int) -> str:
    return f"Class#{qualified_name}|start:{start}|end:{end}"


def _parse_field_declaration(
    node,
    ctx: ParseContext,
    qualified_name: str,
) -> list[dict]:
    options = ctx.options
    modifiers = extract_modifiers(ctx.source_bytes, node)
    if not options.get("includePrivate", True) and "private" in modifiers:
        return []

    type_node = node.child_by_field_name("type")
    type_text = _type_text(type_node, ctx.source_bytes)

    # AST에서 어노테이션 추출 시도
    annotations = _extract_annotations(node, ctx.source_bytes)

    anchor_line = modifier_anchor_line(node) or (node.start_point[0] + 1)
    javadoc = build_javadoc_dict(ctx.lines, anchor_line, options.get("maxJavadocPreviewChars", 0))

    fields: list[dict] = []
    for child in node.named_children:
        if child.type != "variable_declarator":
            continue
        name_node = child.child_by_field_name("name") or first_identifier(child)
        if name_node is None:
            continue
        name = node_text(ctx.source_bytes, name_node)
        start_line = child.start_point[0] + 1
        end_line = child.end_point[0] + 1
        symbol_id = _build_symbol_id("Field", qualified_name, name, start_line, end_line)

        # signatureText 생성
        sig_text = _signature_text(node, ctx.source_bytes)

        # AST에서 추출 실패 시 signatureText에서 추출
        field_annotations = annotations if annotations else _extract_annotations_from_signature(sig_text)

        fields.append(
            {
                "symbolId": symbol_id,
                "kind": "field",
                "name": name,
                "typeText": type_text,
                "modifiers": modifiers,
                "annotations": field_annotations,
                "startLine": start_line,
                "endLine": end_line,
                "javadoc": javadoc,
            }
        )
    return fields


def _parse_constructor_declaration(node, ctx: ParseContext, qualified_name: str) -> Optional[dict]:
    options = ctx.options
    modifiers = extract_modifiers(ctx.source_bytes, node)
    if not options.get("includePrivate", True) and "private" in modifiers:
        return None

    name_node = node.child_by_field_name("name") or first_identifier(node)
    name = node_text(ctx.source_bytes, name_node) if name_node else qualified_name.split(".")[-1]
    params = _parse_parameters(node, ctx.source_bytes)
    throws_list = _throws_list(node, ctx.source_bytes)

    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    detail = f"{name}({','.join(p['typeText'] for p in params)})"
    symbol_id = _build_symbol_id("Ctor", qualified_name, detail, start_line, end_line)

    anchor_line = modifier_anchor_line(node) or start_line
    javadoc = build_javadoc_dict(ctx.lines, anchor_line, options.get("maxJavadocPreviewChars", 0))

    # signatureText 생성
    sig_text = _signature_text(node, ctx.source_bytes)

    # AST에서 어노테이션 추출 시도, 실패 시 signatureText에서 추출
    annotations = _extract_annotations(node, ctx.source_bytes)
    if not annotations:
        annotations = _extract_annotations_from_signature(sig_text)

    return {
        "symbolId": symbol_id,
        "kind": "constructor",
        "name": name,
        "modifiers": modifiers,
        "annotations": annotations,
        "params": params,
        "throws": throws_list,
        "startLine": start_line,
        "endLine": end_line,
        "javadoc": javadoc,
        "signatureText": sig_text,
    }


def _parse_method_declaration(node, ctx: ParseContext, qualified_name: str) -> Optional[dict]:
    options = ctx.options
    modifiers = extract_modifiers(ctx.source_bytes, node)
    if not options.get("includePrivate", True) and "private" in modifiers:
        return None

    name_node = node.child_by_field_name("name") or first_identifier(node)
    if name_node is None:
        return None
    name = node_text(ctx.source_bytes, name_node)

    type_params_node = first_named_child(node, ["type_parameters"])
    type_params_text = _type_text(type_params_node, ctx.source_bytes) if type_params_node else None

    return_type_node = node.child_by_field_name("type")
    if return_type_node is None:
        return_type_node = first_named_child(node, [
            "type",
            "void_type",
            "integral_type",
            "floating_point_type",
            "boolean_type",
        ])
    return_type = _type_text(return_type_node, ctx.source_bytes) or "void"

    params = _parse_parameters(node, ctx.source_bytes)
    throws_list = _throws_list(node, ctx.source_bytes)

    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    detail = f"{name}({','.join(p['typeText'] for p in params)}):{return_type}"
    symbol_id = _build_symbol_id("Method", qualified_name, detail, start_line, end_line)

    anchor_line = modifier_anchor_line(node) or start_line
    javadoc = build_javadoc_dict(ctx.lines, anchor_line, options.get("maxJavadocPreviewChars", 0))

    # signatureText 생성
    sig_text = _signature_text(node, ctx.source_bytes)

    # AST에서 어노테이션 추출 시도, 실패 시 signatureText에서 추출
    annotations = _extract_annotations(node, ctx.source_bytes)
    if not annotations:
        annotations = _extract_annotations_from_signature(sig_text)

    return {
        "symbolId": symbol_id,
        "kind": "method",
        "name": name,
        "returnTypeText": return_type,
        "modifiers": modifiers,
        "annotations": annotations,
        "typeParamsText": type_params_text,
        "params": params,
        "throws": throws_list,
        "startLine": start_line,
        "endLine": end_line,
        "javadoc": javadoc,
        "signatureText": sig_text,
    }


def _parse_class_body(body_node, ctx: ParseContext, qualified_name: str, outer_names: list[str]) -> dict:
    fields: list[dict] = []
    methods: list[dict] = []
    constructors: list[dict] = []
    inner_classes: list[dict] = []

    def handle_member(member) -> None:
        if member.type == "field_declaration" and ctx.options.get("includeFields", True):
            fields.extend(_parse_field_declaration(member, ctx, qualified_name))
            return
        if member.type == "method_declaration":
            method = _parse_method_declaration(member, ctx, qualified_name)
            if method:
                methods.append(method)
            return
        if member.type in ("constructor_declaration", "compact_constructor_declaration") and ctx.options.get(
            "includeConstructors", True
        ):
            ctor = _parse_constructor_declaration(member, ctx, qualified_name)
            if ctor:
                constructors.append(ctor)
            return
        if member.type == "enum_body_declarations":
            for nested in member.named_children:
                handle_member(nested)
            return
        if member.type in CLASS_NODE_KINDS and ctx.options.get("includeInnerClasses", True):
            class_obj = _parse_class_declaration(member, ctx, outer_names)
            if class_obj:
                inner_classes.append(class_obj)

    for child in body_node.named_children:
        handle_member(child)

    return {
        "fields": fields,
        "methods": methods,
        "constructors": constructors,
        "innerClasses": inner_classes,
    }


def _parse_class_declaration(node, ctx: ParseContext, outer_names: list[str]) -> Optional[dict]:
    kind = CLASS_NODE_KINDS.get(node.type)
    if kind is None:
        return None

    name_node = node.child_by_field_name("name") or first_identifier(node)
    if name_node is None:
        return None
    name = node_text(ctx.source_bytes, name_node)

    modifiers = extract_modifiers(ctx.source_bytes, node)
    if not ctx.options.get("includePrivate", True) and "private" in modifiers:
        return None

    qualified_name = _build_qualified_name(ctx.package_name, outer_names, name)

    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1

    anchor_line = modifier_anchor_line(node) or start_line
    javadoc = build_javadoc_dict(ctx.lines, anchor_line, ctx.options.get("maxJavadocPreviewChars", 0))

    body_node = _find_body_node(node)
    body_data = {
        "fields": [],
        "methods": [],
        "constructors": [],
        "innerClasses": [],
    }
    if body_node is not None:
        body_data = _parse_class_body(body_node, ctx, qualified_name, outer_names + [name])

    symbol_id = _class_symbol_id(kind, qualified_name, start_line, end_line)

    # signatureText 생성
    sig_text = _signature_text(node, ctx.source_bytes)

    # AST에서 어노테이션 추출 시도, 실패 시 signatureText에서 추출
    annotations = _extract_annotations(node, ctx.source_bytes)
    if not annotations:
        annotations = _extract_annotations_from_signature(sig_text)

    return {
        "symbolId": symbol_id,
        "kind": kind,
        "name": name,
        "qualifiedName": qualified_name,
        "modifiers": modifiers,
        "annotations": annotations,
        "extends": _extract_extends(node, ctx.source_bytes, kind),
        "implements": _extract_implements(node, ctx.source_bytes, kind),
        "startLine": start_line,
        "endLine": end_line,
        "javadoc": javadoc,
        "signatureText": sig_text,
        "fields": body_data["fields"],
        "constructors": body_data["constructors"],
        "methods": body_data["methods"],
        "innerClasses": body_data["innerClasses"],
    }


def _collect_errors(node) -> list[dict]:
    errors: list[dict] = []

    def walk(n):
        if n.type == "ERROR":
            errors.append(
                {
                    "level": "error",
                    "message": "Parse error",
                    "line": n.start_point[0] + 1,
                }
            )
        for child in n.children:
            walk(child)

    walk(node)
    return errors


def index_java_file(file_path: str, options: Optional[dict] = None, cache_store: Optional[CacheStore] = None) -> dict:
    opts = options or {}
    cache = cache_store or default_cache_store()
    options_key = _options_cache_key(opts)

    try:
        source_bytes = _read_file_bytes(file_path)
    except Exception as exc:
        return {
            "filePath": file_path,
            "language": "java",
            "hash": "",
            "lineCount": 0,
            "classes": [],
            "errors": [
                {
                    "level": "error",
                    "message": f"Failed to read file: {exc}",
                    "line": None,
                }
            ],
        }

    content_hash = _compute_hash(source_bytes)
    cached = cache.load(file_path, content_hash, options_key)
    if cached is not None:
        return cached

    tree = _PARSER.parse(source_bytes)
    root = tree.root_node

    lines = _read_file_lines(source_bytes)
    package = _package_name(root, source_bytes)
    ctx = ParseContext(source_bytes=source_bytes, lines=lines, package_name=package, options=opts)

    classes: list[dict] = []
    for child in root.named_children:
        if child.type in CLASS_NODE_KINDS:
            class_obj = _parse_class_declaration(child, ctx, [])
            if class_obj:
                classes.append(class_obj)

    errors = _collect_errors(root)

    result = {
        "filePath": file_path,
        "language": "java",
        "hash": content_hash,
        "lineCount": len(lines),
        "classes": classes,
        "errors": errors,
    }

    cache.save(file_path, result, options_key)
    return result


def _walk_symbols(index_data: dict) -> list[dict]:
    return [item["symbol"] for item in _walk_symbols_with_class(index_data)]


def _walk_symbols_with_class(index_data: dict) -> list[dict]:
    found: list[dict] = []

    def walk_class(cls: dict) -> None:
        class_name = cls.get("qualifiedName")
        found.append({"symbol": cls, "classQualifiedName": class_name})
        for field in cls.get("fields", []):
            found.append({"symbol": field, "classQualifiedName": class_name})
        for ctor in cls.get("constructors", []):
            found.append({"symbol": ctor, "classQualifiedName": class_name})
        for method in cls.get("methods", []):
            found.append({"symbol": method, "classQualifiedName": class_name})
        for inner in cls.get("innerClasses", []):
            walk_class(inner)

    for cls in index_data.get("classes", []):
        walk_class(cls)

    return found


def find_symbol_by_id(index_data: dict, symbol_id: str) -> Optional[dict]:
    for symbol in _walk_symbols(index_data):
        if symbol.get("symbolId") == symbol_id:
            return symbol
    return None


def find_symbols_in_file(index_data: dict, query: str, options: dict) -> list[dict]:
    match_kind = options.get("matchKind", "any")
    case_sensitive = options.get("caseSensitive", False)

    if not case_sensitive:
        query_cmp = query.lower()
    else:
        query_cmp = query

    def matches(text: str) -> bool:
        if not case_sensitive:
            return query_cmp in text.lower()
        return query_cmp in text

    results: list[dict] = []
    for item in _walk_symbols_with_class(index_data):
        symbol = item["symbol"]
        class_name = item.get("classQualifiedName")
        kind = symbol.get("kind")
        if match_kind != "any" and kind != match_kind:
            continue
        name = symbol.get("name") or symbol.get("qualifiedName") or ""
        if name and matches(name):
            results.append({"symbol": symbol, "classQualifiedName": class_name})
    return results


def find_symbols(root_dir: str, query: str, options: Optional[dict] = None) -> dict:
    opts = options or {}
    cache = default_cache_store()
    max_results = int(opts.get("maxResults", 50))
    index_options = {
        "includePrivate": opts.get("includePrivate", True),
        "includeFields": opts.get("includeFields", True),
        "includeInnerClasses": opts.get("includeInnerClasses", True),
        "includeConstructors": opts.get("includeConstructors", True),
        "maxJavadocPreviewChars": opts.get("maxJavadocPreviewChars", 0),
        "stableIds": opts.get("stableIds", True),
    }

    root = Path(root_dir)
    results: list[dict] = []
    for path in root.rglob("*.java"):
        if len(results) >= max_results:
            break
        index_data = index_java_file(str(path), index_options, cache)
        matches = find_symbols_in_file(index_data, query, opts)
        for match in matches:
            symbol = match["symbol"]
            class_name = match.get("classQualifiedName")
            if symbol.get("kind") == "class":
                qualified = symbol.get("qualifiedName")
            elif class_name and symbol.get("name"):
                qualified = f"{class_name}#{symbol.get('name')}"
            else:
                qualified = symbol.get("qualifiedName") or symbol.get("name")
            results.append(
                {
                    "filePath": index_data.get("filePath", str(path)),
                    "symbolId": symbol.get("symbolId"),
                    "kind": symbol.get("kind"),
                    "qualifiedName": qualified or "",
                    "startLine": symbol.get("startLine"),
                    "endLine": symbol.get("endLine"),
                    "signatureText": symbol.get("signatureText"),
                }
            )
            if len(results) >= max_results:
                break

    return {
        "rootDir": root_dir,
        "query": query,
        "results": results,
    }
