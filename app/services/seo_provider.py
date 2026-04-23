import hashlib
import requests
from requests.auth import HTTPBasicAuth
from abc import ABC, abstractmethod
from flask import current_app
import structlog

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
    """Fetches real metrics from the DataForSEO API."""

    def get_metrics(self, query_text: str, domain: str) -> tuple[int, int]:
        login = current_app.config.get("DATAFORSEO_LOGIN")
        password = current_app.config.get("DATAFORSEO_PASSWORD")

        if not login or not password:
            logger.error("DataForSEO credentials missing. Falling back to 0 metrics.")
            return 0, 0

        logger.info("Fetching REAL SEO data from DataForSEO", query=query_text)

        url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_metrics/live"
        payload = [{
            "keywords": [query_text],
            "location_name": "United States",
            "language_name": "English"
        }]

        try:
            response = requests.post(
                url,
                json=payload,
                auth=HTTPBasicAuth(login, password),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Safely navigate the DataForSEO nested JSON response
            try:
                item = data["tasks"][0]["result"][0]
                if item is None:
                    # Query has no search volume data
                    return 0, 0

                volume = item.get("search_volume", 0)
                # DataForSEO returns difficulty as 0-100 float, we want an int
                difficulty = int(item.get("keyword_difficulty", 0))

                logger.info("DataForSEO Success", volume=volume, difficulty=difficulty)
                return volume, difficulty

            except (IndexError, KeyError, TypeError) as e:
                logger.warning("DataForSEO response unexpected structure", error=str(e), data=data)
                return 0, 0

        except requests.exceptions.RequestException as e:
            logger.error("DataForSEO API call failed", error=str(e))
            # In a production app we might retry, but returning 0 is safe for the pipeline
            return 0, 0


def get_seo_provider() -> BaseSEOProvider:
    """Factory function to inject the correct provider based on configuration."""
    if current_app.config.get("USE_REAL_SEO_DATA"):
        return RealSEOProvider()
    return MockSEOProvider()