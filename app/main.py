import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session, engine, get_db
from app.models import Base, MarketCheck, Opportunity, Product, Supplier, Translation
from app.services.discovery import discover_amazon_products, discover_tiktok_products, run_full_discovery
from app.services.gap_analysis import analyze_all_markets
from app.services.landing_page import export_landing_page, generate_landing_page
from app.services.supplier import find_and_save_suppliers
from app.services.translator import translate_full_set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield


app = FastAPI(title="NewMarkets", lifespan=lifespan)

static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ── Page Routes ──────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    product_count = (await db.execute(select(func.count(Product.id)))).scalar() or 0
    opportunity_count = (await db.execute(select(func.count(Opportunity.id)))).scalar() or 0
    translation_count = (await db.execute(select(func.count(Translation.id)))).scalar() or 0

    top_score_result = await db.execute(select(func.max(Opportunity.gap_score)))
    top_score = top_score_result.scalar() or 0

    stmt = (
        select(Opportunity)
        .options(selectinload(Opportunity.product))
        .order_by(Opportunity.gap_score.desc())
        .limit(10)
    )
    recent_opportunities = (await db.execute(stmt)).scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "product_count": product_count,
        "opportunity_count": opportunity_count,
        "top_score": round(top_score, 1),
        "translation_count": translation_count,
        "recent_opportunities": recent_opportunities,
    })


@app.get("/products", response_class=HTMLResponse)
async def products_list(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).order_by(Product.created_at.desc())
    products = (await db.execute(stmt)).scalars().all()
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
    })


@app.get("/products/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        return HTMLResponse("<h1>Product not found</h1>", status_code=404)

    mc_stmt = select(MarketCheck).where(MarketCheck.product_id == product_id).order_by(MarketCheck.checked_at.desc())
    market_checks = (await db.execute(mc_stmt)).scalars().all()

    opp_stmt = select(Opportunity).where(Opportunity.product_id == product_id).order_by(Opportunity.gap_score.desc())
    opportunities = (await db.execute(opp_stmt)).scalars().all()

    trans_stmt = select(Translation).where(Translation.product_id == product_id).order_by(Translation.created_at.desc())
    translations = (await db.execute(trans_stmt)).scalars().all()

    sup_stmt = select(Supplier).where(Supplier.product_id == product_id)
    suppliers = (await db.execute(sup_stmt)).scalars().all()

    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "market_checks": market_checks,
        "opportunities": opportunities,
        "translations": translations,
        "suppliers": suppliers,
    })


@app.get("/gaps", response_class=HTMLResponse)
async def gaps_view(
    request: Request,
    market: str = Query(default=""),
    status: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Opportunity).options(selectinload(Opportunity.product)).order_by(Opportunity.gap_score.desc())
    if market:
        stmt = stmt.where(Opportunity.market == market)
    if status:
        stmt = stmt.where(Opportunity.status == status)

    opportunities = (await db.execute(stmt)).scalars().all()
    return templates.TemplateResponse("gaps.html", {
        "request": request,
        "opportunities": opportunities,
        "market_filter": market,
        "status_filter": status,
    })


@app.get("/translator", response_class=HTMLResponse)
async def translator_page(
    request: Request,
    product_id: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
):
    products = (await db.execute(select(Product).order_by(Product.title))).scalars().all()

    trans_stmt = (
        select(Translation)
        .options(selectinload(Translation.product))
        .order_by(Translation.created_at.desc())
        .limit(20)
    )
    recent_translations = (await db.execute(trans_stmt)).scalars().all()

    return templates.TemplateResponse("translator.html", {
        "request": request,
        "products": products,
        "selected_product_id": product_id,
        "recent_translations": recent_translations,
    })


# ── API Routes (HTMX) ───────────────────────────────────────


@app.post("/products/add", response_class=HTMLResponse)
async def add_product(
    title: str = Form(...),
    category: str = Form(default=""),
    price_usd: float = Form(default=None),
    source_url: str = Form(default=""),
    image_url: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    product = Product(
        title=title,
        category=category or None,
        price_usd=price_usd,
        source="manual",
        source_url=source_url or None,
        image_url=image_url or None,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return HTMLResponse(
        f'<div class="flash flash-success">Added "{product.title}" (ID: {product.id}). '
        f'<a href="/products/{product.id}" style="color:white;text-decoration:underline">View</a></div>'
    )


@app.post("/api/scrape/amazon", response_class=HTMLResponse)
async def scrape_amazon(db: AsyncSession = Depends(get_db)):
    try:
        count = await discover_amazon_products(db)
        return HTMLResponse(f'<div class="flash flash-success">Amazon scrape complete: {count} new products found.</div>')
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


@app.post("/api/scrape/tiktok", response_class=HTMLResponse)
async def scrape_tiktok(db: AsyncSession = Depends(get_db)):
    try:
        count = await discover_tiktok_products(db)
        return HTMLResponse(f'<div class="flash flash-success">TikTok scrape complete: {count} new products found.</div>')
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


@app.post("/api/scrape/all", response_class=HTMLResponse)
async def scrape_all(db: AsyncSession = Depends(get_db)):
    try:
        result = await run_full_discovery(db)
        return HTMLResponse(
            f'<div class="flash flash-success">Discovery complete: '
            f'{result["amazon_new"]} Amazon + {result["tiktok_new"]} TikTok new products.</div>'
        )
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


@app.post("/api/analyze/{product_id}", response_class=HTMLResponse)
async def analyze_product(product_id: int, db: AsyncSession = Depends(get_db)):
    try:
        opportunities = await analyze_all_markets(db, product_id)
        if not opportunities:
            return HTMLResponse('<div class="flash flash-error">Product not found.</div>')

        rows = ""
        for opp in opportunities:
            color = "var(--success)" if opp.gap_score >= 70 else "var(--warning)" if opp.gap_score >= 40 else "var(--danger)"
            margin = f"{opp.estimated_margin}%" if opp.estimated_margin else "—"
            rows += f"""<tr>
                <td>{opp.market.upper()}</td>
                <td><div class="score-bar" style="width:80px;display:inline-block;vertical-align:middle">
                    <div class="score-fill" style="width:{opp.gap_score}%;background:{color}"></div>
                </div> {opp.gap_score}</td>
                <td>{margin}</td>
                <td><span class="badge badge-blue">{opp.status}</span></td>
            </tr>"""

        return HTMLResponse(
            f'<div class="flash flash-success">Analysis complete for {len(opportunities)} markets.</div>'
            f'<table><thead><tr><th>Market</th><th>Gap Score</th><th>Margin</th><th>Status</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>'
        )
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


@app.post("/api/opportunity/{opp_id}/status", response_class=HTMLResponse)
async def update_opportunity_status(opp_id: int, status: str = Form(...), db: AsyncSession = Depends(get_db)):
    opp = await db.get(Opportunity, opp_id)
    if opp:
        opp.status = status
        await db.commit()
    return HTMLResponse("")


@app.post("/api/translate", response_class=HTMLResponse)
async def translate_copy(
    product_id: int = Form(...),
    language: str = Form(...),
    target_country: str = Form(default=""),
    headline: str = Form(default=""),
    body: str = Form(default=""),
    cta: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    try:
        translations = await translate_full_set(
            db, product_id, language, headline, body, cta, target_country or None
        )
        if not translations:
            return HTMLResponse('<div class="flash flash-error">Translation failed. Check your API key.</div>')

        result_html = ""
        for t in translations:
            result_html += f"""
            <div style="margin-bottom:1rem">
                <div class="flex-between">
                    <span class="badge badge-purple">{t.ad_type}</span>
                    <span class="text-sm text-muted">{t.language.upper()}</span>
                </div>
                <div class="text-sm text-muted mt-1">{t.original_copy}</div>
                <div style="font-size:1.1rem;margin-top:0.5rem;padding:0.75rem;background:var(--surface2);border-radius:0.375rem">{t.translated_copy}</div>
            </div>"""

        return HTMLResponse(f'<div class="flash flash-success">Translated {len(translations)} pieces of copy.</div>{result_html}')
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


@app.post("/api/suppliers/{product_id}", response_class=HTMLResponse)
async def find_suppliers(product_id: int, db: AsyncSession = Depends(get_db)):
    try:
        suppliers = await find_and_save_suppliers(db, product_id)
        if not suppliers:
            return HTMLResponse('<div class="flash flash-error">No suppliers found.</div>')

        rows = ""
        for s in suppliers:
            price = f"${s.unit_price_usd:.2f}" if s.unit_price_usd else "—"
            rows += f"""<tr>
                <td><a href="{s.url}" target="_blank" style="color:var(--primary)">{s.supplier_name[:40]}</a></td>
                <td>{price}</td>
                <td>{s.min_order or '—'}</td>
                <td>{f'{s.shipping_days}d' if s.shipping_days else '—'}</td>
            </tr>"""

        return HTMLResponse(
            f'<div class="flash flash-success">Found {len(suppliers)} suppliers.</div>'
            f'<table><thead><tr><th>Supplier</th><th>Price</th><th>MOQ</th><th>Ship</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>'
        )
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


@app.post("/api/landing/{product_id}", response_class=HTMLResponse)
async def generate_landing(
    product_id: int,
    language: str = Form(...),
    market: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        filepath = await export_landing_page(db, product_id, language, market)
        if filepath:
            html = await generate_landing_page(db, product_id, language, market)
            return HTMLResponse(
                f'<div class="flash flash-success">Landing page exported to {filepath}</div>'
                f'<iframe srcdoc=\'{html}\' style="width:100%;height:400px;border:1px solid var(--border);border-radius:0.375rem;margin-top:1rem"></iframe>'
            )
        return HTMLResponse('<div class="flash flash-error">Could not generate landing page. Add translations first.</div>')
    except Exception as e:
        return HTMLResponse(f'<div class="flash flash-error">Error: {e}</div>')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
