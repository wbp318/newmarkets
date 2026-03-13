import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.scrapers.amazon import AmazonProduct, scrape_best_sellers, scrape_movers_shakers
from app.scrapers.tiktok import TikTokProduct, scrape_trending_products

logger = logging.getLogger(__name__)


async def discover_amazon_products(db: AsyncSession, category: str | None = None) -> int:
    """Scrape Amazon and save new products. Returns count of new products."""
    best_sellers = await scrape_best_sellers(category)
    movers = await scrape_movers_shakers(category)
    all_products = best_sellers + movers

    new_count = 0
    for ap in all_products:
        new_count += await _upsert_product(db, ap, source="amazon")

    await db.commit()
    logger.info(f"Amazon discovery complete: {new_count} new products")
    return new_count


async def discover_tiktok_products(db: AsyncSession) -> int:
    """Scrape TikTok trending and save new products."""
    trending = await scrape_trending_products()
    new_count = 0
    for tp in trending:
        new_count += await _upsert_tiktok(db, tp)

    await db.commit()
    logger.info(f"TikTok discovery complete: {new_count} new products")
    return new_count


async def run_full_discovery(db: AsyncSession) -> dict:
    """Run all discovery scrapers."""
    amazon_count = await discover_amazon_products(db)
    tiktok_count = await discover_tiktok_products(db)
    return {"amazon_new": amazon_count, "tiktok_new": tiktok_count}


async def _upsert_product(db: AsyncSession, ap: AmazonProduct, source: str) -> int:
    """Insert or update a product from Amazon. Returns 1 if new, 0 if updated."""
    stmt = select(Product).where(
        Product.title == ap.title,
        Product.source == source,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.last_seen = datetime.now(timezone.utc)
        existing.price_usd = ap.price_usd or existing.price_usd
        existing.source_rank = ap.rank
        return 0

    product = Product(
        title=ap.title,
        category=ap.category,
        image_url=ap.image_url,
        price_usd=ap.price_usd,
        source=source,
        source_url=ap.source_url,
        source_rank=ap.rank,
    )
    db.add(product)
    return 1


async def _upsert_tiktok(db: AsyncSession, tp: TikTokProduct) -> int:
    """Insert or update a TikTok product."""
    stmt = select(Product).where(
        Product.title == tp.title,
        Product.source == "tiktok",
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.last_seen = datetime.now(timezone.utc)
        return 0

    product = Product(
        title=tp.title,
        category=tp.category,
        image_url=tp.image_url,
        source="tiktok",
        source_url=tp.source_url,
        source_rank=tp.rank,
    )
    db.add(product)
    return 1
