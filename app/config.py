import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./newmarkets.db")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MERCADOLIBRE_APP_ID: str = os.getenv("MERCADOLIBRE_APP_ID", "")
    MERCADOLIBRE_CLIENT_SECRET: str = os.getenv("MERCADOLIBRE_CLIENT_SECRET", "")

    # Scraper settings
    SCRAPE_INTERVAL_HOURS: int = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # Target markets
    MARKETS = {
        "mx": {"name": "Mexico", "currency": "MXN", "lang": "es", "ml_site": "MLM"},
        "co": {"name": "Colombia", "currency": "COP", "lang": "es", "ml_site": "MCO"},
        "br": {"name": "Brazil", "currency": "BRL", "lang": "pt", "ml_site": "MLB"},
        "ar": {"name": "Argentina", "currency": "ARS", "lang": "es", "ml_site": "MLA"},
    }

    # Exchange rates (fallback, updated via API later)
    EXCHANGE_RATES = {
        "MXN": 17.15,
        "COP": 3950.0,
        "BRL": 4.95,
        "ARS": 875.0,
    }


settings = Settings()
