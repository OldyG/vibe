from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_server import handlers

mcp = FastMCP("mcp-java-indexer")


@mcp.tool()
def java_index(filePath: str, options: dict | None = None) -> dict:
    return handlers.java_index(filePath, options)


@mcp.tool()
def java_read_range(
    filePath: str, startLine: int, endLine: int, options: dict | None = None
) -> dict:
    return handlers.java_read_range(filePath, startLine, endLine, options)


@mcp.tool()
def java_read_javadoc(filePath: str, symbolId: str, options: dict | None = None) -> dict:
    return handlers.java_read_javadoc(filePath, symbolId, options)


@mcp.tool()
def java_find_symbol(rootDir: str, query: str, options: dict | None = None) -> dict:
    return handlers.java_find_symbol(rootDir, query, options)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
