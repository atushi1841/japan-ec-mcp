# japan-ec-mcp

**Japanese E-Commerce & Secondary Market Search — MCP server**

Claude / Cursor / VS Code などの AI クライアントから、日本の主要マーケットプレース（メルカリ、ヤフオク、駿河屋、楽天、価格.com）の価格・在庫・動向を直接問い合わせる Model Context Protocol (MCP) サーバーです。

- 作者: atushi1841
- ライセンス: MIT
- MCP 規格: FastMCP 2.x（stdio / HTTP 両対応）
- 関連プロジェクト: [Kensho](https://github.com/atushi1841/kensho) — X（Twitter）懸賞自動化

---

## Tools（MCP ツール一覧）

| ツール名 | 機能 | 対象プラットフォーム |
|---|---|---|
| `search_japan_marketplace` | キーワードで商品価格・在庫を横断検索 | Mercari, Yahoo Auctions, Suruga-ya |
| `get_japan_resale_guidance` | 中古リセール市場の調達指針（TCG / カメラ / 高級時計 / 高級ブランド / フィギュア） | 5カテゴリ |

### Tool 1 — `search_japan_marketplace`

```python
result = await mcp.call_tool(
    "search_japan_marketplace",
    {"keyword": "ポケモンカード 151", "platform": "all", "limit": 10}
)
```

- `platform`: `"mercari" | "yahoo" | "surugaya" | "all"`（default: `all`）
- 戻り値: `{query, platforms_searched, results: [{platform, search_url, notes, recommended_actor}]}`

### Tool 2 — `get_japan_resale_guidance`

```python
result = await mcp.call_tool(
    "get_japan_resale_guidance",
    {"category": "tcg", "keywords": ["ポケモン", "151"]}
)
```

- `category`: `"tcg" | "camera" | "luxury" | "figure" | "watch"`
- 戻り値: 各カテゴリの市場特性・推奨調達チャネル・Apify Actor 導線

---

## MCP 接続例

### 1. 標準入出力（stdio）— Claude Desktop 等

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "japan-ec-mcp": {
      "command": "python",
      "args": ["/path/to/japan-ec-mcp/server.py"]
    }
  }
}
```

### 2. HTTP サーバーモード

```bash
cd japan-ec-mcp
pip install fastmcp
python server.py --http --port 8000
```

HTTP エンドポイント確認:

```bash
curl http://localhost:8000/mcp/tools | jq .
```

### 3. Python から直接 import

```python
from japan_ec_mcp.server import mcp
# FastMCP インスタンスを直接組み込める
```

### 4. n8n / Apify Workflow から（HTTP 経由）

Apify の **Webhook** node で `POST /mcp` に JSON-RPC を投げる構成で利用可。
（サンプルワークフローは開発中・MCP の HTTP mode は 2026-10 実装）

---

## Related Apify Actors

この MCP サーバーは Apify Store の 86 Actors と連携し、**実際にデータを取りたい場面では該当する Actor を併用**することを想定しています。PPE（pay-per-event）課金・無料枠あり。

### 主力 Marketplace Scrapers

| Actor | 用途 | 価格 |
|---|---|---|
| [mercari-japan-search-scraper](https://apify.com/fruitful_quintessence/mercari-japan-search-scraper) | メルカリ日本版の商品検索・価格抽出 | PPE |
| [yahoo-auctions-japan-scraper](https://apify.com/fruitful_quintessence/yahoo-auctions-japan-scraper) | ヤフオク入札・落札履歴抽出 | PPE |
| [surugaya-japan-hobby-prices](https://apify.com/fruitful_quintessence/surugaya-japan-hobby-prices) | 駿河屋（ホビー・TCG）中古価格 | PPE |
| [japan-kakaku-price-search](https://apify.com/fruitful_quintessence/japan-kakaku-price-search) | 価格.com の家電・日用品価格比較 | PPE |
| [rakuten-japan-mcp](https://apify.com/fruitful_quintessence/rakuten-japan-mcp) | 楽天市場の商品・価格データ | PPE |

### 中古 / 専門店 Scrapers

| Actor | カテゴリ |
|---|---|
| [mandarake-auction-scraper](https://apify.com/fruitful_quintessence/mandarake-auction-scraper) | 万代・中古フィギュア・プラモ |
| [kitamura-japan-used-camera-scraper](https://apify.com/fruitful_quintessence/kitamura-japan-used-camera-scraper) | 中古カメラ（キタムラ） |
| [jackroad-used-watch-scraper](https://apify.com/fruitful_quintessence/jackroad-used-watch-scraper) | 中古時計（ジャックロード） |
| [komehyo-japan-brand-scraper](https://apify.com/fruitful_quintessence/komehyo-japan-brand-scraper) | 高級ブランド（こめはよ） |
| [tackleberry-japan-fishing-tackle-scraper](https://apify.com/fruitful_quintessence/tackleberry-japan-fishing-tackle-scraper) | フィッシングタックル（タックルベリー） |

### Japan Market MCP 系列

- [japan-market-mcp](https://apify.com/fruitful_quintessence/japan-market-mcp) — 総合マクロ経済・市場データ
- [japan-anime-figure-price-data](https://apify.com/fruitful_quintessence/japan-anime-figure-price-data) — アニメフィギュア価格
- [japan-anime-figure-demand-features](https://apify.com/fruitful_quintessence/japan-anime-figure-demand-features) — アニメフィギュア需要特徴量

---

## Quickstart

```bash
# 1. クローン
git clone https://github.com/atushi1841/japan-ec-mcp.git
cd japan-ec-mcp

# 2. 依存
pip install fastmcp

# 3. stdio mode で起動（Claude Desktop 等から接続）
python server.py

# 4. HTTP mode で起動（別プロセスから接続）
python server.py --http --port 8000
```

### 動作確認

```bash
python server.py --http --port 8000 &
sleep 2
curl -s -X POST http://localhost:8000/mcp/tools/list \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.tools[].name'
```

---

## MCP 公開レジストリ登録状況

| レジストリ | 状態 | 備考 |
|---|---|---|
| MCP 公式レジストリ | ✅ 登録済み | `io.github.atushi1841/japan-ec-mcp` |
| Smithery.ai | 📝 【要ユーザー対応】 未登録 | `mcp/kensho-*/smithery.yaml` テンプレあり（本サーバーはテンプレ未作成・要追加） |
| mcp.so | 📝 【要ユーザー対応】 未登録 | YAML テンプレは Kensho 側に `mcp_so_configs/` 予定 |

**収益化経路**: GitHub README → Smithery（未登録）→ Apify Store（86 Actors・PPE課金）への流入。
Smithery 登録は API で自動実行不可のためユーザー手動操作待ち（【要ユーザー対応】タグ継続）。

---

## 収益ゲート（この README の役割）

| 項目 | 内容 |
|---|---|
| 誰が買う | MCP クライアント利用者（Claude/Cursor/VS Code + 日本マーケットデータ需要層） |
| どのチャネルで届くか | GitHub README 直接流入 → Smithery / mcp.so（要ユーザー対応）経由で Apify PPE 86本へ |
| 30日で何を測れるか | README への apify.com リンク数 >= 4（現在 >= 10）・Smithery api 200（未登録継続） |
| 既存何を再利用 | 既存 README（2tools）+ Apify 86 actors URL 群 + smithery.yaml テンプレ |

---

## License

MIT License. See [Kensho](https://github.com/atushi1841/kensho) project for the full stack.

## Install via Smithery

Connect this MCP server to your AI client (Claude Desktop, Cursor, VS Code) in one command:

```bash
npx @smithery/cli install atushi1841/japan-ec-mcp --client claude
```

Replace `claude` with `cursor`, `vscode`, or `cline` for other clients.

Alternatively, install directly from the [Smithery registry](https://smithery.ai/server/atushi1841/japan-ec-mcp).

> **Note:** Smithery server listing is pending verification. Once verified, this server will appear in search results with useCount tracking.
