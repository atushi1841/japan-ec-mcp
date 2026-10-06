# Japan E-Commerce & Secondary Market Search MCP

MCP server exposing Japanese e-commerce pricing, used market trends, and product availability search across major platforms.

## Tools

- **search_japan_marketplace**: Search Mercari, Yahoo Auctions, and Suruga-ya listings
- **get_japan_resale_guidance**: Get sourcing guidance for specific product categories (TCG, camera, luxury, figure, watch)

## Usage

```bash
python server.py
```

Or as an HTTP server:

```bash
python server.py --http
```

## Related Apify Actors

- [mercari-japan-search-scraper](https://apify.com/fruitful_quintessence/mercari-japan-search-scraper)
- [yahoo-auctions-japan-scraper](https://apify.com/fruitful_quintessence/yahoo-auctions-japan-scraper)
- [surugaya-japan-hobby-prices](https://apify.com/fruitful_quintessence/surugaya-japan-hobby-prices)
- [japan-kakaku-price-search](https://apify.com/fruitful_quintessence/japan-kakaku-price-search)
