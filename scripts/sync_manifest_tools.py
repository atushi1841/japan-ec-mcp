"""稼働中MCPサーバー(stdio)の tools/list から manifest.json の tools 配列を同期する。

Smitheryのstdio公開APIは各ツールに inputSchema を要求する（欠けると400）。
サーバー実装を正として manifest を生成するため、手書きせずここで同期する。
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BUNDLE_DIR = sys.argv[1] if len(sys.argv) > 1 else "/mnt/d/Project2/kensho/mcp_servers/japan_ec_mcp"
MANIFEST = os.path.join(BUNDLE_DIR, "manifest.json")


async def fetch_tools() -> list[dict]:
    params = StdioServerParameters(
        command=sys.executable,
        args=["src/stdio_main.py"],
        env=dict(os.environ),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            out: list[dict] = []
            for t in tools.tools:
                entry: dict = {"name": t.name}
                if t.description:
                    entry["description"] = t.description
                schema = t.inputSchema or {"type": "object", "properties": {}}
                entry["inputSchema"] = schema
                out.append(entry)
            return out


def main() -> None:
    tools = asyncio.run(fetch_tools())
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["tools"] = tools
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("tools同期:", len(tools), "件 ->", MANIFEST)
    for t in tools:
        print(" -", t["name"], "| schema keys:", list(t["inputSchema"].get("properties", {})))


if __name__ == "__main__":
    main()