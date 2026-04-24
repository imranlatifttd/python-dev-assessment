import hashlib
import requests
from requests.auth import HTTPBasicAuth
from abc import ABC, abstractmethod
from flask import current_app
import structlog
import re
import time

logger = structlog.get_logger(__name__)


class BaseSEOProvider(ABC):
    """Abstract base class for SEO data providers"""

    @abstractmethod
    def get_metrics(self, query_text: str, domain: str) -> tuple[int, int]:
        """Returns (volume, difficulty) for a given query"""
        pass


class MockSEOProvider(BaseSEOProvider):
    """Generates deterministic mock metrics using a stable hash"""

    def get_metrics(self, query_text: str, domain: str) -> tuple[int, int]:
        logger.info("Using mocked SEO data", query=query_text)
        hash_obj = hashlib.md5(query_text.encode('utf-8'))
        hash_int = int(hash_obj.hexdigest(), 16)

        volume = (hash_int % 9991) + 10
        difficulty = (hash_int // 10000) % 101

        return volume, difficulty


class RealSEOProvider(BaseSEOProvider):
    """Fetches real metrics from the DataForSEO API"""

    def get_metrics(self, query_text: str, domain: str) -> tuple[int, int]:
        login = current_app.config.get("DATAFORSEO_LOGIN")
        password = current_app.config.get("DATAFORSEO_PASSWORD")

        if not login or not password:
            logger.error("DataForSEO credentials missing. Falling back to 0 metrics.")
            return 0, 0

        # sanitize for Google Ads, remove punctuation and cap at 10 words
        clean_query = re.sub(r'[^\w\s-]', '', query_text).strip()
        clean_query = " ".join(clean_query.split()[:10])[:80]

        logger.info("Fetching REAL SEO data from DataForSEO", original=query_text, sanitized=clean_query)

        url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
        payload = [{
            "keywords": [clean_query],
            "location_name": "United States",
            "language_code": "en"
        }]

        # throttle to stay under the 12 requests/minute free-tier limit
        time.sleep(5.1)

        try:
            response = requests.post(
                url,
                json=payload,
                auth=HTTPBasicAuth(login, password),
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            # defensive parsing to prevent NoneType errors
            task = data.get("tasks", [{}])[0]

            # if DataForSEO throws a specific error like rate limit or word count
            if task.get("status_code") != 20000:
                logger.warning("DataForSEO API rejected query",
                               status=task.get("status_code"),
                               msg=task.get("status_message"))
                return 0, 0

            result = task.get("result")
            if not result or result[0] is None:
                return 0, 0

            item = result[0]

            volume = int(item.get("search_volume") or 0)
            difficulty = int(item.get("competition_index") or 0)

            logger.info("DataForSEO Success", volume=volume, difficulty=difficulty)
            return volume, difficulty

        except Exception as e:
            logger.error("DataForSEO API call failed", error=str(e))
            return 0, 0


def get_seo_provider() -> BaseSEOProvider:
    """Factory function to inject the correct provider based on configuration."""
    if current_app.config.get("USE_REAL_SEO_DATA"):
        return RealSEOProvider()
    return MockSEOProvider()