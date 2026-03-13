import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import MarketCheck, Opportunity, Product
from app.scrapers.mercadolibre import convert_to_usd, search_product

logger = logging.getLogger(__name__)


async def check_market(db: AsyncSession, product_id: int, market: str) -> MarketCheck | None:
    """Search for a product in a LATAM market and record results."""
    product = await db.get(Product, product_id)
    if not product:
        return None

    results = await search_product(product.title, market)

    market_info = settings.MARKETS.get(market, {})
    currency = market_info.get("currency", "USD")

    found = len(results) > 0
    competitor_count = len(results)
    avg_price_local = None
    avg_price_usd = None

    if results:
        prices = [r.price_local for r in results if r.price_local > 0]
        if prices:
            avg_price_local = sum(prices) / len(prices)
            avg_price_usd = convert_to_usd(avg_price_local, currency)

    check = MarketCheck(
        product_id=product_id,
        market=market,
        found=found,
        competitor_count=competitor_count,
        avg_price_local=avg_price_local,
        avg_price_usd=avg_price_usd,
        platform="mercadolibre",
    )
    db.add(check)
    await db.commit()
    await db.refresh(check)
    return check


async def analyze_gap(db: AsyncSession, product_id: int, market: str) -> Opportunity | None:
    """Calculate gap score for a product in a market and create/update opportunity."""
    product = await db.get(Product, product_id)
    if not product:
        return None

    # Get latest market check
    stmt = (
        select(MarketCheck)
        .where(MarketCheck.product_id == product_id, MarketCheck.market == market)
        .order_by(MarketCheck.checked_at.desc())
    )
    result = await db.execute(stmt)
    check = result.scalar_one_or_none()

    if not check:
        # Run market check first
        check = await check_market(db, product_id, market)
        if not check:
            return None

    gap_score = _calculate_gap_score(product, check)
    estimated_margin = _estimate_margin(product, check)

    # Upsert opportunity
    stmt = select(Opportunity).where(
        Opportunity.product_id == product_id,
        Opportunity.market == market,
    )
    result = await db.execute(stmt)
    opp = result.scalar_one_or_none()

    if opp:
        opp.gap_score = gap_score
        opp.estimated_margin = estimated_margin
        opp.trend_velocity = product.trend_score
        opp.updated_at = datetime.now(timezone.utc)
    else:
        opp = Opportunity(
            product_id=product_id,
            market=market,
            gap_score=gap_score,
            trend_velocity=product.trend_score,
            estimated_margin=estimated_margin,
        )
        db.add(opp)

    await db.commit()
    await db.refresh(opp)
    return opp


async def analyze_all_markets(db: AsyncSession, product_id: int) -> list[Opportunity]:
    """Analyze gap for a product across all target markets."""
    opportunities = []
    for market in settings.MARKETS:
        opp = await analyze_gap(db, product_id, market)
        if opp:
            opportunities.append(opp)
    return opportunities


def _calculate_gap_score(product: Product, check: MarketCheck) -> float:
    """Calculate opportunity gap score (0-100).

    Higher score = better opportunity. Factors:
    - Low competitor count = more opportunity
    - No presence = highest score boost
    - Price arbitrage potential
    - Product trend score
    """
    score = 0.0

    # Competition factor (0-40 points)
    if not check.found:
        score += 40  # Product not found = huge opportunity
    elif check.competitor_count <= 3:
        score += 30
    elif check.competitor_count <= 10:
        score += 20
    elif check.competitor_count <= 25:
        score += 10
    else:
        score += 5

    # Price arbitrage factor (0-30 points)
    if product.price_usd and check.avg_price_usd:
        markup = (check.avg_price_usd - product.price_usd) / product.price_usd
        if markup > 1.0:
            score += 30  # >100% markup potential
        elif markup > 0.5:
            score += 25
        elif markup > 0.3:
            score += 20
        elif markup > 0.1:
            score += 10
    elif not check.found:
        score += 20  # Can't compare prices, but no competition

    # Trend factor (0-30 points)
    trend = product.trend_score or 0
    if trend >= 80:
        score += 30
    elif trend >= 60:
        score += 25
    elif trend >= 40:
        score += 20
    elif trend >= 20:
        score += 10
    else:
        score += 5

    return min(round(score, 1), 100.0)


def _estimate_margin(product: Product, check: MarketCheck) -> float | None:
    """Estimate profit margin percentage."""
    if not product.price_usd:
        return None

    if check.avg_price_usd and check.avg_price_usd > product.price_usd:
        return round((check.avg_price_usd - product.price_usd) / product.price_usd * 100, 1)

    # Default estimate: 40% markup potential if no market data
    if not check.found:
        return 40.0
    return None
