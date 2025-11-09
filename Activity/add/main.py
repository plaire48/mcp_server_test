from fastmcp import FastMCP
import os

mcp = FastMCP(name="AppsToolServer")


@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    return a - b

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "1015"))
    path = os.getenv("MCP_PATH", "/")
    mcp.run(transport="streamable-http", host=host, port=port, path=path)