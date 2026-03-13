# NewMarkets

Cross-market e-commerce arbitrage toolkit. Finds winning products trending in the US (Amazon, TikTok Shop), identifies gaps in Latin American markets (Mexico, Colombia, Brazil, Argentina), and provides tools to launch — ad copy translation, supplier sourcing, and landing page generation.

---

## Quick Start (Windows Executable)

**No install required.** Download and double-click.

1. Go to [Releases](https://github.com/wbp318/newmarkets/releases/latest)
2. Download **NewMarkets.exe**
3. Double-click it — a black terminal window opens and your web browser launches automatically
4. Use the app in your browser at `http://localhost:8000`
5. To stop, close the black terminal window

Your data is saved in a file called `newmarkets.db` that appears in the same folder as the exe. As long as you don't delete that file, your products, opportunities, and translations are all kept between sessions.

### Setting Up the Translator (Optional)

The ad copy translator uses Claude AI to translate your ad headlines, body text, and calls-to-action into Spanish and Portuguese. To enable it:

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. In the same folder where you saved `NewMarkets.exe`, create a new text file
3. Rename it to `.env` (the file has no name, just the extension)
4. Open it with Notepad and paste this line, replacing the placeholder with your real key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
5. Save and close. Next time you run NewMarkets, translations will work.

Everything else (product tracking, scrapers, market gap analysis, supplier search) works without an API key.

---

## How to Use

### Dashboard

The main screen you see when the app opens. It shows:

- **Stats** — how many products you're tracking, how many opportunities you've found, your top gap score, and how many translations you've done
- **Add Product** — type in a product name, price, category, and optionally a URL and image link, then click "Add Product"
- **Run Scrapers** — click "Scrape Amazon", "Scrape TikTok", or "Run All Scrapers" to automatically find trending US products and add them to your list
- **Top Opportunities** — a quick view of your highest-scoring market gaps

### Products

Click **Products** in the top navigation bar. This shows every product you've added or discovered through scrapers.

- Each row shows the product name, category, price, where it came from (Amazon, TikTok, or manually added), and its trend score
- Click **View** to see the full detail page for a product
- Click **Analyze** to run a market gap check across all 4 Latin American markets

### Product Detail Page

When you click into a single product, you get the full picture:

- **Product Info** — image, price, source, rank, trend score
- **Market Analysis** — click "Run Analysis (All Markets)" to search MercadoLibre in Mexico, Colombia, Brazil, and Argentina for competing products. It shows whether the product was found, how many competitors exist, and what they charge
- **Opportunities** — after analysis runs, you'll see a gap score (0–100) for each market. Higher score = better opportunity. You can change the status of each opportunity using the dropdown (New, Researching, Launching, Active, Passed)
- **Suppliers** — click "Find Suppliers" to search AliExpress for sourcing options with prices and minimum order quantities
- **Translations** — shows any translations you've created. Click "Translate Ad Copy" to go to the translator
- **Landing Page** — pick a language and market, click "Generate & Export" to create a localized landing page. It saves as a standalone HTML file in an `exports` folder next to the exe

### Opportunities

Click **Opportunities** in the navigation bar to see all your market gaps ranked by score.

- Filter by market (Mexico, Colombia, Brazil, Argentina) or status (New, Researching, etc.)
- The gap score considers three things:
  - **Competition** — fewer competitors in the target market = higher score
  - **Price arbitrage** — if the product sells for more in the target market than you can source it, the score goes up
  - **Trend velocity** — products trending harder in the US get a boost
- Change the status of any opportunity right from the table using the dropdown

### Translator

Click **Translator** in the navigation bar. This is where you create localized ad copy.

1. Pick a product from the dropdown
2. Choose the target language (Spanish for MX/CO/AR, Portuguese for BR)
3. Choose the target country — this adjusts the translation for local slang and cultural fit
4. Type your English headline, body copy, and call-to-action
5. Click "Translate with Claude" — the AI-translated versions appear on the right
6. Recent translations are saved and shown at the bottom of the page

### Landing Page Generator

From any product detail page, scroll to the bottom:

1. Pick a language and market
2. Click "Generate & Export"
3. A preview appears in the page, and a standalone HTML file is saved to the `exports` folder
4. You can open that HTML file in any browser or upload it as a landing page

---

## Features

- **Product Discovery** — Scrape Amazon Best Sellers / Movers & Shakers and TikTok Creative Center for trending products
- **Market Gap Analysis** — Search MercadoLibre across 4 LATAM markets, score opportunities by competition level, price arbitrage, and trend velocity
- **Google Trends Comparison** — Compare US vs target market search interest with pytrends
- **Ad Copy Translator** — Translate headlines, body copy, and CTAs to Spanish/Portuguese via Claude API with country-specific localization
- **Supplier Finder** — Search AliExpress for sourcing options with price and MOQ data
- **Landing Page Generator** — Generate localized landing pages from templates, export as standalone HTML

## Target Markets

| Code | Country   | Currency | MercadoLibre Site |
|------|-----------|----------|-------------------|
| MX   | Mexico    | MXN      | MLM               |
| CO   | Colombia  | COP      | MCO               |
| BR   | Brazil    | BRL      | MLB               |
| AR   | Argentina | ARS      | MLA               |

---

## Business — 318ecom LLC

This project is operated under **318ecom LLC**, a Louisiana limited liability company domiciled in East Carroll Parish.

The `business/` folder contains everything needed to form and run the LLC:

| Document | What It Covers |
|----------|---------------|
| [`00_MASTER_CHECKLIST.md`](business/00_MASTER_CHECKLIST.md) | Step-by-step formation checklist, estimated startup costs (~$135), important contacts and phone numbers |
| [`01_ARTICLES_OF_ORGANIZATION.md`](business/01_ARTICLES_OF_ORGANIZATION.md) | Exactly what to fill in on the LA Secretary of State website — name, purpose, registered agent, NAICS code, fees |
| [`02_OPERATING_AGREEMENT.md`](business/02_OPERATING_AGREEMENT.md) | Full operating agreement template — management, capital contributions, profit allocation, dissolution, indemnification |
| [`03_EIN_APPLICATION.md`](business/03_EIN_APPLICATION.md) | Walk-through of every question on the IRS online EIN form, tax classification options (disregarded entity vs S-Corp) |
| [`04_LOUISIANA_COMPLIANCE.md`](business/04_LOUISIANA_COMPLIANCE.md) | Annual report, state income tax, sales tax, self-employment tax, quarterly estimated payments, record keeping calendar |
| [`05_BANK_ACCOUNT_SETUP.md`](business/05_BANK_ACCOUNT_SETUP.md) | What to bring to the bank, local options near Lake Providence, online banks (Mercury, Relay, Bluevine), 30% tax savings rule |

### Formation Order

1. File Articles of Organization with LA Secretary of State ($100 online)
2. Sign the Operating Agreement (keep with your records)
3. Apply for EIN at irs.gov (free, takes 5 minutes)
4. Open a business bank account (bring EIN letter + Articles + Operating Agreement + ID)
5. Register with Louisiana Department of Revenue on LaTAP
6. Start selling

### Key Compliance Dates

| What | When |
|------|------|
| LA Annual Report ($30) | Your LLC formation anniversary |
| Federal + State Tax Returns | April 15 |
| Quarterly Estimated Taxes | April 15, June 15, September 15, January 15 |

---

## Developer Setup

If you want to run from source instead of the exe:

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

### Building the Executable

```bash
pip install pyinstaller
python -m PyInstaller newmarkets.spec --clean
# Output: dist/NewMarkets.exe
```

### Project Structure

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

### Tech Stack

- Python + FastAPI + Jinja2 + HTMX
- SQLite + SQLAlchemy 2.0 (async)
- Claude API (ad copy translation)
- MercadoLibre public API
- pytrends, httpx, BeautifulSoup
