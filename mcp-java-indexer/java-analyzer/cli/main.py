from __future__ import annotations

import argparse
import json

from parser.indexer import find_symbols, index_java_file
from parser.readers import read_range


def _print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=True, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="java-analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index a Java file")
    index_parser.add_argument("file", help="Path to Java file")
    index_parser.add_argument("--no-private", action="store_true", help="Exclude private symbols")
    index_parser.add_argument("--no-fields", action="store_true", help="Exclude fields")
    index_parser.add_argument("--no-inner", action="store_true", help="Exclude inner classes")
    index_parser.add_argument("--no-constructors", action="store_true", help="Exclude constructors")
    index_parser.add_argument(
        "--javadoc-preview-chars", type=int, default=0, help="Include Javadoc preview chars"
    )

    range_parser = subparsers.add_parser("range", help="Read a range of lines")
    range_parser.add_argument("file", help="Path to Java file")
    range_parser.add_argument("start", type=int, help="Start line (1-based)")
    range_parser.add_argument("end", type=int, help="End line (1-based)")
    range_parser.add_argument("--no-line-numbers", action="store_true", help="Omit line numbers")
    range_parser.add_argument("--max-chars", type=int, default=20000, help="Max output characters")

    find_parser = subparsers.add_parser("find", help="Find symbols in a directory")
    find_parser.add_argument("--root", required=True, help="Root directory")
    find_parser.add_argument("--query", required=True, help="Symbol name query")
    find_parser.add_argument("--kind", default="any", help="class|method|field|any")
    find_parser.add_argument("--max-results", type=int, default=50, help="Max results")
    find_parser.add_argument("--case-sensitive", action="store_true", help="Case sensitive search")

    args = parser.parse_args()

    if args.command == "index":
        options = {
            "includePrivate": not args.no_private,
            "includeFields": not args.no_fields,
            "includeInnerClasses": not args.no_inner,
            "includeConstructors": not args.no_constructors,
            "maxJavadocPreviewChars": args.javadoc_preview_chars,
        }
        result = index_java_file(args.file, options)
        _print_json(result)
        return

    if args.command == "range":
        options = {
            "includeLineNumbers": not args.no_line_numbers,
            "maxChars": args.max_chars,
        }
        result = read_range(args.file, args.start, args.end, options)
        _print_json(result)
        return

    if args.command == "find":
        options = {
            "matchKind": args.kind,
            "maxResults": args.max_results,
            "caseSensitive": args.case_sensitive,
        }
        result = find_symbols(args.root, args.query, options)
        _print_json(result)
        return


if __name__ == "__main__":
    main()

