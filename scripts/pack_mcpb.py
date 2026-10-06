"""server.mcpb（Smithery公開用MCPBバンドル）を作成する。

`npx @anthropic-ai/mcpb pack` は manifest.json を MCPB公式スキーマで厳格検証する。
しかしSmitheryのstdio公開APIは各ツールに inputSchema を必須としている
（ServerCard.tools[].inputSchema が required、実測: 欠けると400
 "Invalid input: expected object, received undefined" ×ツール数）。
MCPB公式スキーマは tools[].additionalProperties=false のため inputSchema を許さず、
両者は両立しない（Smithery上の他社stdioサーバーも inputSchema 付きで公開されている）。

そこで本スクリプトは .mcpbignore を自前で適用してZIP化する（検証はスキップ）。
manifest.json の tools は scripts/sync_manifest_tools.py で稼働中サーバーから同期すること。
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "server.mcpb")


def load_ignore(root: str) -> list[str]:
    path = os.path.join(root, ".mcpbignore")
    patterns: list[str] = []
    if not os.path.exists(path):
        return patterns
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line.rstrip("/"))
    return patterns


def ignored(rel: str, is_dir: bool, patterns: list[str]) -> bool:
    rel = rel.replace(os.sep, "/")
    for p in patterns:
        if rel == p or rel.startswith(p + "/"):
            return True
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p):
            return True
        if is_dir and fnmatch.fnmatch(rel + "/", p + "/"):
            return True
    return False


def main() -> None:
    manifest_path = os.path.join(ROOT, "manifest.json")
    manifest = json.load(open(manifest_path, encoding="utf-8"))

    missing = [k for k in ("manifest_version", "name", "version", "description", "author", "server") if k not in manifest]
    if missing:
        raise SystemExit(f"manifest.json 必須フィールド欠落: {missing}")
    tools = manifest.get("tools") or []
    bad = [t.get("name") for t in tools if not isinstance(t.get("inputSchema"), dict)]
    if bad:
        raise SystemExit(
            "Smitheryは全ツールに inputSchema を要求します。欠落: "
            f"{bad} → scripts/sync_manifest_tools.py を実行してください"
        )

    patterns = load_ignore(ROOT)
    entries: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        rel_dir = "" if rel_dir == "." else rel_dir
        dirnames[:] = [d for d in dirnames if not ignored(os.path.join(rel_dir, d), True, patterns)]
        for fn in filenames:
            rel = os.path.join(rel_dir, fn) if rel_dir else fn
            if ignored(rel, False, patterns):
                continue
            entries.append(rel)
    entries.sort()

    if "manifest.json" not in entries:
        raise SystemExit("manifest.json がバンドル対象に含まれていません")

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in entries:
            z.write(os.path.join(ROOT, rel), rel)

    size = os.path.getsize(OUTPUT)
    with zipfile.ZipFile(OUTPUT) as z:
        unpacked = sum(i.file_size for i in z.infolist())
    print(f"出力: {OUTPUT}")
    print(f"ファイル数: {len(entries)} / パッケージ {size/1024:.1f}KB / 展開後 {unpacked/1024/1024:.1f}MB")
    print("tools:", [t["name"] for t in tools])
    for rel in entries:
        print("  ", rel)


if __name__ == "__main__":
    main()