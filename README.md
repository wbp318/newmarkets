# NewMarkets

Cross-market e-commerce arbitrage toolkit. Finds winning products trending in the US (Amazon, TikTok Shop), identifies gaps in Latin American markets (Mexico, Colombia, Brazil, Argentina), and provides tools to launch — ad copy translation, supplier sourcing, and landing page generation.

## Features

- **Product Discovery** — Scrape Amazon Best Sellers / Movers & Shakers and TikTok Creative Center for trending products
- **Market Gap Analysis** — Search MercadoLibre across 4 LATAM markets, score opportunities by competition level, price arbitrage, and trend velocity
- **Google Trends Comparison** — Compare US vs target market search interest with pytrends
- **Ad Copy Translator** — Translate headlines, body copy, and CTAs to Spanish/Portuguese via Claude API with country-specific localization
- **Supplier Finder** — Search AliExpress for sourcing options with price and MOQ data
- **Landing Page Generator** — Generate localized landing pages from templates, export as standalone HTML

## Tech Stack

- Python + FastAPI + Jinja2 + HTMX
- SQLite + SQLAlchemy 2.0 (async)
- Claude API (ad copy translation)
- MercadoLibre public API
- pytrends, httpx, BeautifulSoup

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run
python -m app.main
# Server starts at http://localhost:8000
```

## Project Structure

```
app/
├── main.py              # FastAPI routes + HTMX endpoints
├── config.py            # Settings and API keys
├── database.py          # SQLAlchemy async engine
├── models.py            # Product, MarketCheck, Opportunity, Translation, Supplier
├── scrapers/
│   ├── amazon.py        # Best Sellers + Movers & Shakers
│   ├── tiktok.py        # Creative Center trending
│   ├── mercadolibre.py  # LATAM market search
│   └── google_trends.py # US vs target market comparison
├── services/
│   ├── discovery.py     # Product discovery orchestration
│   ├── gap_analysis.py  # Market gap scoring (0-100)
│   ├── translator.py    # Claude API ad copy translation
│   ├── supplier.py      # AliExpress supplier search
│   └── landing_page.py  # Localized landing page generator
└── templates/           # Jinja2 + HTMX frontend
```

## Target Markets

| Code | Country   | Currency | MercadoLibre Site |
|------|-----------|----------|-------------------|
| MX   | Mexico    | MXN      | MLM               |
| CO   | Colombia  | COP      | MCO               |
| BR   | Brazil    | BRL      | MLB               |
| AR   | Argentina | ARS      | MLA               |
