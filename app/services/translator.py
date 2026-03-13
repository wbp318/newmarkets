import logging

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Product, Translation

logger = logging.getLogger(__name__)

AD_TYPES = ["headline", "body", "cta"]

SYSTEM_PROMPT = """You are an expert e-commerce copywriter and translator specializing in Latin American markets.
You understand cultural nuances, local slang, and what drives purchases in each country.
Your translations are not literal — they are localized adaptations that feel native."""


async def translate_ad_copy(
    db: AsyncSession,
    product_id: int,
    language: str,
    original_copy: str,
    ad_type: str,
    target_country: str | None = None,
) -> Translation | None:
    """Translate ad copy using Claude API.

    Args:
        product_id: Product ID
        language: Target language (es or pt)
        original_copy: English source text
        ad_type: headline, body, or cta
        target_country: Optional country for localization (Mexico, Colombia, Brazil, Argentina)
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not configured")
        return None

    product = await db.get(Product, product_id)
    if not product:
        return None

    lang_name = "Spanish" if language == "es" else "Portuguese (Brazilian)"
    country_note = f" for the {target_country} market" if target_country else ""

    prompts = {
        "headline": f"Translate this e-commerce ad headline to {lang_name}{country_note}. "
                    f"Keep it punchy, attention-grabbing, under 60 characters. "
                    f"Product: {product.title}\n\nHeadline: {original_copy}",
        "body": f"Translate this e-commerce ad body copy to {lang_name}{country_note}. "
                f"Maintain the persuasive tone, adapt cultural references. "
                f"Product: {product.title}\n\nBody copy: {original_copy}",
        "cta": f"Translate this call-to-action to {lang_name}{country_note}. "
               f"Make it compelling and action-oriented. "
               f"Product: {product.title}\n\nCTA: {original_copy}",
    }

    prompt = prompts.get(ad_type, prompts["body"])

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        translated = message.content[0].text.strip()

        translation = Translation(
            product_id=product_id,
            language=language,
            original_copy=original_copy,
            translated_copy=translated,
            ad_type=ad_type,
        )
        db.add(translation)
        await db.commit()
        await db.refresh(translation)
        return translation

    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None


async def translate_full_set(
    db: AsyncSession,
    product_id: int,
    language: str,
    headline: str,
    body: str,
    cta: str,
    target_country: str | None = None,
) -> list[Translation]:
    """Translate a full set of ad copy (headline + body + CTA)."""
    translations = []
    for ad_type, copy in [("headline", headline), ("body", body), ("cta", cta)]:
        if copy:
            t = await translate_ad_copy(db, product_id, language, copy, ad_type, target_country)
            if t:
                translations.append(t)
    return translations
