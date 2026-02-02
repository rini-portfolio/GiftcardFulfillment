import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("fiserv")


class FiservError(Exception):
    pass


class FiservClient:
    """Lightweight client for Fiserv issuing APIs.

    - Retries network/5xx errors
    - Raises FiservError on failures
    - Returns giftcardId string on success
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 5, retries: int = 3, backoff: float = 0.5):
        if not base_url:
            raise ValueError("base_url is required")
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def issue(self, email: str, amount: float) -> str:
        try:
            resp = self.session.post(
                self.base_url, json={"email": email, "amount": amount}, headers=self.headers, timeout=self.timeout
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.exception("Fiserv request failed")
            raise FiservError("Error contacting Fiserv") from e

        try:
            body = resp.json()
        except ValueError as e:
            logger.exception("Invalid JSON from Fiserv")
            raise FiservError("Invalid response from Fiserv") from e

        giftcard_id = body.get("giftcardId") or body.get("id") or body.get("giftcard_id")
        if not giftcard_id:
            logger.error("Missing giftcard id in Fiserv response: %s", body)
            raise FiservError("Missing giftcardId in Fiserv response")

        return giftcard_id
