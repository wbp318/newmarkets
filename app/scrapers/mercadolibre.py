import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# MercadoLibre public API base
ML_API_BASE = "https://api.mercadolibre.com"


@dataclass
class MLSearchResult:
    title: str
    price_local: float
    currency: str
    seller_count: int
    url: str
    image_url: str | None
    condition: str | None


async def search_product(query: str, market: str) -> list[MLSearchResult]:
    """Search for a product on MercadoLibre in a given market.

    Args:
        query: Product search term
        market: Market code (mx, co, br, ar)
    """
    market_info = settings.MARKETS.get(market)
    if not market_info:
        logger.error(f"Unknown market: {market}")
        return []

    site_id = market_info["ml_site"]
    url = f"{ML_API_BASE}/sites/{site_id}/search"
    params = {"q": query, "limit": 50}

    results = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("results", []):
                results.append(MLSearchResult(
                    title=item.get("title", ""),
                    price_local=item.get("price", 0.0),
                    currency=item.get("currency_id", market_info["currency"]),
                    seller_count=data.get("paging", {}).get("total", 0),
                    url=item.get("permalink", ""),
                    image_url=item.get("thumbnail"),
                    condition=item.get("condition"),
                ))

            logger.info(f"ML search '{query}' in {market}: {len(results)} results")
    except Exception as e:
        logger.error(f"Error searching MercadoLibre {market} for '{query}': {e}")

    return results


async def get_category_trends(market: str, category_id: str = "MLM1055") -> dict:
    """Get category trends from MercadoLibre."""
    market_info = settings.MARKETS.get(market)
    if not market_info:
        return {}

    site_id = market_info["ml_site"]
    url = f"{ML_API_BASE}/sites/{site_id}/categories/{category_id}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Error getting ML category trends: {e}")
        return {}


def convert_to_usd(price_local: float, currency: str) -> float | None:
    """Convert local price to USD using configured exchange rates."""
    rate = settings.EXCHANGE_RATES.get(currency)
    if rate and rate > 0:
        return round(price_local / rate, 2)
    return None
