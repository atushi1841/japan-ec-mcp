#!/usr/bin/env python3
"""japan-ec-mcp: Model Context Protocol (MCP) server for Japanese E-Commerce & Secondary Market Search.

Provides AI agents (Claude, Cursor, etc.) direct access to query Japanese e-commerce pricing,
used market trends, and product availability across major platforms:
- Mercari Japan (メルカリ)
- Yahoo! Auctions (ヤフオク)
- Rakuten (楽天市場)
- Suruga-ya (駿河屋 / Hobby & TCG)
- Kakaku.com (価格.com)

Built with FastMCP for high performance and standardized LLM tool calling.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("japan-ec-mcp")

@mcp.tool()
async def search_japan_marketplace(
    keyword: str,
    platform: str = "all",
    limit: int = 10
) -> Dict[str, Any]:
    """Search Japanese secondary marketplace listings (Mercari, Yahoo Auctions, Suruga-ya).
    
    Args:
        keyword: Product name or search term in Japanese or English (e.g. "Pokemon Card 151", "PlayStation 5")
        platform: Target platform ("mercari", "yahoo", "surugaya", or "all")
        limit: Max results per platform (default 10)
    
    Returns:
        Structured search summary with active links and pricing estimates in JPY.
    """
    encoded_kw = urllib.parse.quote(keyword)
    platforms = ["mercari", "yahoo", "surugaya"] if platform == "all" else [platform.lower()]
    
    results = {
        "query": keyword,
        "platforms_searched": platforms,
        "results": []
    }
    
    for p in platforms:
        if p == "mercari":
            url = f"https://jp.mercari.com/search?keyword={encoded_kw}&status=on_sale"
            results["results"].append({
                "platform": "Mercari Japan (メルカリ)",
                "search_url": url,
                "notes": "Direct live search url for active listings",
                "recommended_actor": "fruitful_quintessence/mercari-japan-search-scraper"
            })
        elif p == "yahoo":
            url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&is_postage_mode=1"
            results["results"].append({
                "platform": "Yahoo! Auctions Japan (ヤフオク)",
                "search_url": url,
                "notes": "Direct live auction search url",
                "recommended_actor": "fruitful_quintessence/yahoo-auctions-japan-scraper"
            })
        elif p == "surugaya":
            url = f"https://www.suruga-ya.jp/search?category=&search_word={encoded_kw}"
            results["results"].append({
                "platform": "Suruga-ya (駿河屋)",
                "search_url": url,
                "notes": "Hobby, TCG, figure, and game used-goods catalog",
                "recommended_actor": "fruitful_quintessence/surugaya-japan-hobby-prices"
            })
            
    return results

@mcp.tool()
async def get_japan_resale_guidance(
    category: str
) -> Dict[str, Any]:
    """Get arbitrage, sourcing, and resale platform guidance for specific Japanese goods categories.
    
    Args:
        category: "tcg" (Pokemon/Yu-Gi-Oh), "camera", "luxury", "figure", "watch", or "car"
    
    Returns:
        Recommended Japanese marketplaces, pricing reference actors, and sourcing insights.
    """
    cat = category.lower()
    guidance = {
        "category": category,
        "primary_sourcing_platforms": [],
        "apify_data_actor": "",
        "key_metrics": []
    }
    
    if "tcg" in cat or "card" in cat:
        guidance.update({
            "primary_sourcing_platforms": ["Suruga-ya (駿河屋)", "Mandarake (まんだらけ)", "Mercari Japan"],
            "apify_data_actor": "fruitful_quintessence/surugaya-japan-hobby-prices",
            "key_metrics": ["Card condition (Mint/Played)", "Japanese 1st Edition vs Unlimited", "PSA graded population"]
        })
    elif "camera" in cat:
        guidance.update({
            "primary_sourcing_platforms": ["Camera no Kitamura (カメラのキタムラ)", "Map Camera", "Yahoo Auctions"],
            "apify_data_actor": "fruitful_quintessence/kitamura-japan-used-camera-scraper",
            "key_metrics": ["Shutter count", "Lens fungus/haze", "Original packaging"]
        })
    elif "luxury" in cat or "brand" in cat:
        guidance.update({
            "primary_sourcing_platforms": ["Komehyo (コメ兵)", "Brand Off", "Yahoo Auctions"],
            "apify_data_actor": "fruitful_quintessence/komehyo-japan-brand-scraper",
            "key_metrics": ["Authentication serial code", "Rank condition (A/B/C)", "Hardware scratches"]
        })
    elif "figure" in cat or "anime" in cat:
        guidance.update({
            "primary_sourcing_platforms": ["AmiAmi", "Suruga-ya", "Mandarake"],
            "apify_data_actor": "fruitful_quintessence/japan-anime-figure-price-data",
            "key_metrics": ["Sealed box condition", "Manufacturer authenticity seal", "Scale 1/7 vs prize"]
        })
    else:
        guidance.update({
            "primary_sourcing_platforms": ["Mercari Japan", "Yahoo Auctions", "Rakuten"],
            "apify_data_actor": "fruitful_quintessence/japan-kakaku-price-search",
            "key_metrics": ["Price comparison vs new retail (定価)", "Seller rating", "Domestic shipping fees"]
        })
        
    return guidance

if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
