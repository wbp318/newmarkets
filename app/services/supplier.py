import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Product, Supplier

logger = logging.getLogger(__name__)


@dataclass
class SupplierResult:
    name: str
    url: str
    price: float | None
    min_order: int | None
    image_url: str | None


async def search_aliexpress(query: str) -> list[SupplierResult]:
    """Search AliExpress for suppliers. Basic scraper approach."""
    results = []
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }

    search_url = f"https://www.aliexpress.com/wholesale?SearchText={query.replace(' ', '+')}"

    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(search_url)
            resp.raise_for_status()
            results = _parse_aliexpress(resp.text)
            logger.info(f"AliExpress search '{query}': {len(results)} results")
    except Exception as e:
        logger.error(f"Error searching AliExpress for '{query}': {e}")

    return results


def _parse_aliexpress(html: str) -> list[SupplierResult]:
    """Parse AliExpress search results page."""
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # AliExpress uses React hydration, so HTML parsing is best-effort
    items = soup.select("[class*='product-card'], [class*='list--gallery']")

    for item in items[:20]:
        title_el = item.select_one("h3, [class*='title'], a[title]")
        if not title_el:
            continue

        name = title_el.get_text(strip=True) or title_el.get("title", "")
        if not name:
            continue

        price = None
        price_el = item.select_one("[class*='price']")
        if price_el:
            price_text = price_el.get_text(strip=True)
            # Extract numeric price
            import re
            match = re.search(r"[\d.]+", price_text.replace(",", ""))
            if match:
                try:
                    price = float(match.group())
                except ValueError:
                    pass

        url = ""
        link = item.select_one("a[href]")
        if link:
            href = link["href"]
            if href.startswith("//"):
                href = f"https:{href}"
            url = href

        results.append(SupplierResult(
            name=name[:500],
            url=url,
            price=price,
            min_order=None,
            image_url=None,
        ))

    return results


async def find_and_save_suppliers(db: AsyncSession, product_id: int) -> list[Supplier]:
    """Search for suppliers and save results."""
    product = await db.get(Product, product_id)
    if not product:
        return []

    results = await search_aliexpress(product.title)
    suppliers = []

    for r in results[:10]:  # Save top 10
        supplier = Supplier(
            product_id=product_id,
            supplier_name=r.name,
            platform="aliexpress",
            url=r.url,
            unit_price_usd=r.price,
            min_order=r.min_order,
        )
        db.add(supplier)
        suppliers.append(supplier)

    await db.commit()
    return suppliers
