import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)

CREATIVE_CENTER_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en"


@dataclass
class TikTokProduct:
    title: str
    category: str | None
    image_url: str | None
    source_url: str
    rank: int


async def scrape_trending_products() -> list[TikTokProduct]:
    """Scrape TikTok Creative Center for trending product ads.

    Note: TikTok's Creative Center is JS-heavy. This scraper gets what it can
    from the initial HTML. For full data, a headless browser would be needed.
    """
    products = []
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(CREATIVE_CENTER_URL)
            resp.raise_for_status()
            products = _parse_creative_center(resp.text)
            logger.info(f"Scraped {len(products)} trending items from TikTok")
    except Exception as e:
        logger.error(f"Error scraping TikTok Creative Center: {e}")

    return products


def _parse_creative_center(html: str) -> list[TikTokProduct]:
    """Parse TikTok Creative Center page. Best-effort since it's JS-rendered."""
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # Look for ad cards or product entries
    cards = soup.select("[class*='card']") or soup.select("[class*='item']")

    for rank, card in enumerate(cards[:50], start=1):
        title_el = card.select_one("h3, h4, [class*='title'], [class*='name']")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title or len(title) < 3:
            continue

        image_url = None
        img = card.select_one("img")
        if img:
            image_url = img.get("src") or img.get("data-src")

        source_url = ""
        link = card.select_one("a[href]")
        if link:
            source_url = link["href"]

        products.append(TikTokProduct(
            title=title[:500],
            category=None,
            image_url=image_url,
            source_url=source_url,
            rank=rank,
        ))

    return products
