import logging
from dataclasses import dataclass

from pytrends.request import TrendReq

logger = logging.getLogger(__name__)


@dataclass
class TrendComparison:
    keyword: str
    us_interest: float
    target_interest: float
    gap_ratio: float  # Higher = more opportunity (popular in US, not in target)


def compare_interest(keywords: list[str], target_geo: str = "MX") -> list[TrendComparison]:
    """Compare Google Trends interest between US and a target market.

    Args:
        keywords: Up to 5 search terms
        target_geo: Target country code (MX, CO, BR, AR)
    """
    if not keywords:
        return []

    keywords = keywords[:5]  # Google Trends limit
    results = []

    try:
        pytrends = TrendReq(hl="en-US", tz=360)

        # Get US interest
        pytrends.build_payload(keywords, cat=0, timeframe="today 3-m", geo="US")
        us_data = pytrends.interest_over_time()

        # Get target market interest
        pytrends.build_payload(keywords, cat=0, timeframe="today 3-m", geo=target_geo)
        target_data = pytrends.interest_over_time()

        for kw in keywords:
            us_avg = float(us_data[kw].mean()) if kw in us_data.columns else 0.0
            target_avg = float(target_data[kw].mean()) if kw in target_data.columns else 0.0

            # Gap ratio: high US interest + low target interest = opportunity
            if target_avg > 0:
                gap_ratio = us_avg / target_avg
            elif us_avg > 0:
                gap_ratio = us_avg * 2  # No target interest = big opportunity
            else:
                gap_ratio = 0.0

            results.append(TrendComparison(
                keyword=kw,
                us_interest=round(us_avg, 1),
                target_interest=round(target_avg, 1),
                gap_ratio=round(gap_ratio, 2),
            ))

        logger.info(f"Trends comparison for {keywords} (US vs {target_geo}): done")
    except Exception as e:
        logger.error(f"Error comparing trends: {e}")

    return results


def get_related_queries(keyword: str, geo: str = "US") -> dict:
    """Get related rising/top queries for a keyword."""
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe="today 3-m", geo=geo)
        related = pytrends.related_queries()
        result = related.get(keyword, {})
        return {
            "top": result.get("top", {}).to_dict("records") if hasattr(result.get("top"), "to_dict") else [],
            "rising": result.get("rising", {}).to_dict("records") if hasattr(result.get("rising"), "to_dict") else [],
        }
    except Exception as e:
        logger.error(f"Error getting related queries for '{keyword}': {e}")
        return {"top": [], "rising": []}
