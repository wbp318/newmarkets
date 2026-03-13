import logging
import os

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, Supplier, Translation

logger = logging.getLogger(__name__)

LANDING_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "landing")


def get_landing_env() -> Environment:
    return Environment(loader=FileSystemLoader(LANDING_DIR), autoescape=True)


async def generate_landing_page(
    db: AsyncSession,
    product_id: int,
    language: str,
    market: str,
) -> str | None:
    """Generate a localized landing page for a product.

    Returns rendered HTML string or None on failure.
    """
    product = await db.get(Product, product_id)
    if not product:
        return None

    # Get translations for this product/language
    stmt = select(Translation).where(
        Translation.product_id == product_id,
        Translation.language == language,
    )
    result = await db.execute(stmt)
    translations = result.scalars().all()

    copy = {}
    for t in translations:
        copy[t.ad_type] = t.translated_copy

    # Get supplier info
    stmt = select(Supplier).where(Supplier.product_id == product_id).limit(3)
    result = await db.execute(stmt)
    suppliers = result.scalars().all()

    env = get_landing_env()
    try:
        template = env.get_template("default.html")
    except Exception:
        logger.error("Landing page template not found")
        return None

    html = template.render(
        product=product,
        headline=copy.get("headline", product.title),
        body=copy.get("body", ""),
        cta=copy.get("cta", "Buy Now" if language == "en" else "Comprar Ahora"),
        language=language,
        market=market,
        suppliers=suppliers,
    )
    return html


async def export_landing_page(
    db: AsyncSession,
    product_id: int,
    language: str,
    market: str,
    output_dir: str = "exports",
) -> str | None:
    """Generate and save landing page as standalone HTML file."""
    html = await generate_landing_page(db, product_id, language, market)
    if not html:
        return None

    os.makedirs(output_dir, exist_ok=True)
    filename = f"landing_{product_id}_{market}_{language}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"Exported landing page: {filepath}")
    return filepath
