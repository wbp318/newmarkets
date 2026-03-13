import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)

BEST_SELLER_URLS = {
    "Health & Household": "https://www.amazon.com/Best-Sellers-Health-Household/zgbs/hpc",
    "Beauty & Personal Care": "https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty",
    "Home & Kitchen": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden",
    "Sports & Outdoors": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods",
}

MOVERS_SHAKERS_URLS = {
    "Health & Household": "https://www.amazon.com/gp/movers-and-shakers/hpc",
    "Beauty & Personal Care": "https://www.amazon.com/gp/movers-and-shakers/beauty",
    "Home & Kitchen": "https://www.amazon.com/gp/movers-and-shakers/home-garden",
    "Sports & Outdoors": "https://www.amazon.com/gp/movers-and-shakers/sporting-goods",
}


@dataclass
class AmazonProduct:
    title: str
    price_usd: float | None
    image_url: str | None
    source_url: str
    rank: int
    category: str


async def scrape_best_sellers(category: str | None = None) -> list[AmazonProduct]:
    """Scrape Amazon Best Sellers. If category is None, scrape all target categories."""
    urls = BEST_SELLER_URLS
    if category and category in urls:
        urls = {category: urls[category]}

    products = []
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        for cat_name, url in urls.items():
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                items = _parse_best_sellers_page(resp.text, cat_name)
                products.extend(items)
                logger.info(f"Scraped {len(items)} products from Amazon {cat_name}")
            except Exception as e:
                logger.error(f"Error scraping Amazon {cat_name}: {e}")

    return products


async def scrape_movers_shakers(category: str | None = None) -> list[AmazonProduct]:
    """Scrape Amazon Movers & Shakers for trending products."""
    urls = MOVERS_SHAKERS_URLS
    if category and category in urls:
        urls = {category: urls[category]}

    products = []
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        for cat_name, url in urls.items():
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                items = _parse_best_sellers_page(resp.text, cat_name)
                products.extend(items)
                logger.info(f"Scraped {len(items)} movers from Amazon {cat_name}")
            except Exception as e:
                logger.error(f"Error scraping Amazon movers {cat_name}: {e}")

    return products


def _parse_best_sellers_page(html: str, category: str) -> list[AmazonProduct]:
    """Parse an Amazon Best Sellers / Movers & Shakers page."""
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # Amazon uses various selectors; try the most common ones
    items = soup.select("div[data-asin]")
    if not items:
        items = soup.select(".zg-item-immersion")

    for rank, item in enumerate(items[:50], start=1):
        try:
            # Title
            title_el = item.select_one("a.a-link-normal span") or item.select_one(".p13n-sc-truncated")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            # Price
            price = None
            price_el = item.select_one(".p13n-sc-price") or item.select_one("span.a-price span.a-offscreen")
            if price_el:
                price_text = price_el.get_text(strip=True).replace("$", "").replace(",", "")
                try:
                    price = float(price_text)
                except ValueError:
                    pass

            # Image
            image_url = None
            img_el = item.select_one("img")
            if img_el:
                image_url = img_el.get("src")

            # Link
            source_url = ""
            link_el = item.select_one("a.a-link-normal")
            if link_el and link_el.get("href"):
                href = link_el["href"]
                if href.startswith("/"):
                    href = f"https://www.amazon.com{href}"
                source_url = href

            products.append(AmazonProduct(
                title=title[:500],
                price_usd=price,
                image_url=image_url,
                source_url=source_url,
                rank=rank,
                category=category,
            ))
        except Exception as e:
            logger.debug(f"Error parsing Amazon item: {e}")

    return products
